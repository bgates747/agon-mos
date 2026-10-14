#!/usr/bin/env ruby
require 'fileutils'
require 'json'
out=ARGV.fetch(0);FileUtils.mkdir_p(out)
# Reuse the passed benchmark and byte comparator; adapt stress reply ordering.
raise 'Benchmark generation failed' unless system('ruby','experiments/uart0-bench/packets.rb',"#{out}/bench")
raise 'Stress generation failed' unless system('ruby','experiments/uart0-stress/packets.rb',"#{out}/stress")
# MOS exposes GP as a last-value latch, so allow only one outstanding reply.
# Put each GP request before its 256-byte write to retain a TX overlap window.
info=JSON.parse(File.read("#{out}/stress/expected.json"))
inc=File.read("#{out}/stress/packets.inc")
4.times do |n|
 bytes=File.binread("#{out}/stress/packet#{n}.bin").bytes
 prefix=6+3*info.fetch('pause_frames')[n]
 acknowledged=bytes.take(prefix)
 bytes.drop(prefix).each_slice(268) do |piece|
  acknowledged+=piece.last(4)+piece.take(264)
 end
 block="packet#{n}:\n"+acknowledged.each_slice(24).map{|b|"    DB #{b.join(',')}\n"}.join+"packet#{n}_end:\n"
 inc=inc.sub(/packet#{n}:.*?packet#{n}_end:\n/m,block)
 File.binwrite("#{out}/stress/packet#{n}.bin",acknowledged.pack('C*'))
 require 'digest'
 info['packet_sha256'][n]=Digest::SHA256.hexdigest(acknowledged.pack('C*'))
end
info['reply_protocol']='one outstanding GP request; request precedes each 256-byte write'
info['reply_rounds']=32
File.write("#{out}/stress/packets.inc",inc)
File.write("#{out}/stress/expected.json",JSON.pretty_generate(info)+"\n")
FileUtils.cp("#{out}/bench/checks.bin","#{out}/checks.bin")
%w[bench stress].each do |kind|
 source=File.read("experiments/uart0-#{kind}/#{kind}.asm")
 controls="    DB \"UTC1\"\n"
 %w[result_name baseline_name failure_name].each do |name|
  line=source.lines.find{|l|l.start_with?("#{name}:")}
  text=line[/DB "([^"]+)"/,1]
  controls+=line+"    DS #{16-text.size-1}\n"
  source=source.sub(line,'')
 end
 source=source.sub("    DB \"MOS\",0,1\n", "    DB \"MOS\",0,1\n"+controls)
 if kind=='stress'
  first=source.index("    call tx_reserve\n",source.index("selected:\n"))
  last=source.index("record_case:\n",first)
  source[first...last]=<<~'ASM'
    ; First round includes clear/pause prefix; later rounds are 268 bytes.
    ld a,(case_index)
    ld hl,pause_digits
    ld de,0
    ld e,a
    add hl,de
    ld a,(hl)
    sub a,'0'
    ld e,a
    add a,a
    add a,e
    add a,6
    ld e,a
    ld hl,268
    add hl,de
    ld (round_size),hl
    ld hl,0
    ld (accepted),hl
round_loop:
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket),hl
    ex de,hl
    ld hl,(source)
    ld bc,(round_size)
    call tx_publish
    or a,a
    jp nz,failed
observe:
    call observe_reply
    call tx_poll_drain
    cp a,1
    jr z,observe
    or a,a
    jp nz,failed
    ld de,(ticket)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld de,(round_size)
    or a,a
    sbc hl,de
    jp nz,failed
    ld hl,(accepted)
    add hl,de
    ld (accepted),hl
    ld de,(ticket)
    call tx_reap
    or a,a
    jp nz,failed
    ; Never request the next token until this one is observed.
    ; Timeout is safe here: this round has reached TEMT and released RAM.
    call clock_read
    ld (reply_started),hl
wait_round:
    call observe_reply
    ld a,(sequence_error)
    or a,a
    jr nz,rounds_done
    ld a,(round_index)
    inc a
    ld b,a
    ld a,(observed)
    cp a,b
    jr z,round_done
    call clock_read
    ld de,(reply_started)
    or a,a
    sbc hl,de
    ld de,2400
    or a,a
    sbc hl,de
    jr c,wait_round
    ld a,2
    ld (sequence_error),a
    jr rounds_done
round_done:
    ld hl,(source)
    ld de,(round_size)
    add hl,de
    ld (source),hl
    ld hl,268
    ld (round_size),hl
    ld a,(round_index)
    inc a
    ld (round_index),a
    cp a,32
    jp nz,round_loop
rounds_done:
    call tx_close
    or a,a
    jp nz,failed
ASM
  source=source.sub('    ld (observed),a', "    ld (observed),a\n    ld (round_index),a")
  source=source.sub('source_size: DB', "round_size: DB 0,0,0\nround_index: DB 0\nsource_size: DB")
  source=source.sub('8192 bytes + 32 replies...', '8192 bytes, 32 acknowledged replies...')
 end
 # Return safely to the suite on ordinary test failure. A CTS stall retains RAM.
 if kind=='bench'
  source=source.sub('    ld (tx_diag_take+1),hl',"    ld (tx_diag_take+1),hl\n    ld a,1\n    ld (api_installed),a")
  source=source.sub('saved_sp: DB',"api_installed: DB 0\nsaved_sp: DB")
  source=source.sub("failed:\n    ei", "failed:\n    ld a,(api_installed)\n    or a,a\n    jr z,save_failure\nfailed_drain:\n    call tx_poll_drain\n    cp a,1\n    jr z,failed_drain\n    call tx_close\nsave_failure:\n    ei")
 end
 source=source.sub(/failed_hold:\n    halt\n    jr failed_hold/, "failed_hold:\n    ld sp,(saved_sp)\n    pop iy\n    pop ix\n    pop hl\n    pop de\n    pop bc\n    pop af\n    ld hl,1\n    ret")
 source=source.gsub('reset required','returning to suite').gsub('reset required; return card for inspection','returning to suite')
 source=source.gsub('saved in baseline.dat','saved in numbered baseline').gsub('saving bench.dat','saving numbered result')
 File.write("#{out}/#{kind}/#{kind}.asm",source)
 link=File.read("experiments/uart0-#{kind}/#{kind}.linkcmd").sub('$040000 : $04FFFF','$080000 : $08FFFF')
 File.write("#{out}/#{kind}/#{kind}.linkcmd",link)
end
FileUtils.cp('build/uart0-mos/MOS.bin',"#{out}/MOS.bin")
FileUtils.cp('build/uart0-mos/MOS.map',"#{out}/MOS.map")
margin=File.binread('build/uart0-margin/margin.bin')
raise 'Rebuild margin child for private command E7 first' unless margin.include?("\x17\x00\xe7\x02".b)
FileUtils.cp('build/uart0-margin/margin.bin',"#{out}/margin.bin")
require 'digest'
sources=%w[experiments/uart0-suite/src/main.c experiments/uart0-suite/src/uart.src experiments/uart0-suite/entry.asm]+%w[bench stress].map{|k|"#{out}/#{k}/#{k}.asm"}
identity=Digest::SHA256.hexdigest(sources.map{|p|File.binread(p)}.join)[0,16]
File.write("#{out}/identity.h", "#define SUITE_BUILD_ID \"#{identity}\"\n")
# Fold in the earlier installed-MOS ordering/masked-IFF/exit and ADL=0 fixtures.
FileUtils.mkdir_p("#{out}/api")
s=File.read('experiments/uart0-mos/app.asm')
controls="    DB \"UTC1\"\n"
%w[result_name baseline_name failure_name].each do |name|
 line=s.lines.find{|l|l.start_with?("#{name}:")} || "baseline_name: DB \"api-base.dat\",0\n"
 text=line[/DB "([^"]+)"/,1];controls+=line+"    DS #{16-text.size-1}\n";s=s.sub(line,'')
end
s=s.sub("    DB \"MOS\",0,1\n","    DB \"MOS\",0,1\n"+controls)
s=s.sub('    ld (diagnostics),hl',"    ld (diagnostics),hl\n    ld a,1\n    ld (api_installed),a")
s=s.sub('saved_sp: DB',"api_installed: DB 0\nsaved_sp: DB")
s=s.sub("failed:\n    ei", "failed:\n    ld a,(api_installed)\n    or a,a\n    jr z,save_failure\nfailed_drain:\n    call tx_poll_drain\n    cp a,1\n    jr z,failed_drain\n    call tx_close\nsave_failure:\n    ei")
s=s.sub(/failed_hold:\n    halt\n    jr failed_hold/,"failed_hold:\n    ld sp,(saved_sp)\n    pop iy\n    pop ix\n    pop hl\n    pop de\n    pop bc\n    pop af\n    ld hl,1\n    ret")
File.write("#{out}/api/app.asm",s)
File.write("#{out}/api/app.linkcmd",File.read('experiments/uart0-mos/app.linkcmd').sub('$040000 : $04FFFF','$080000 : $08FFFF'))
FileUtils.cp('build/uart0-mos/packets.inc',"#{out}/api/packets.inc")
short=File.read('experiments/uart0-mos/short.asm').sub('cp a,4','cp a,8').sub("    halt\n    jr failed", "    ld hl,1\n    ld sp,(saved_sps)\n    ret.lis")
File.write("#{out}/api/short.asm",short)
FileUtils.cp('experiments/uart0-mos/short.linkcmd',"#{out}/api/short.linkcmd")
# Include the final adapted children in the build identity.
sources=%w[experiments/uart0-suite/src/main.c experiments/uart0-suite/src/uart.src experiments/uart0-suite/entry.asm]+%w[bench/bench stress/stress api/app api/short].map{|k|"#{out}/#{k}.asm"}+%w[bench stress api].map{|k|"#{out}/#{k}/packets.inc"}
identity=Digest::SHA256.hexdigest(sources.map{|p|File.binread(p)}.join)[0,16]
File.write("#{out}/identity.h", "#define SUITE_BUILD_ID \"#{identity}\"\n#define SUITE_STRESS_BYTES {#{info['packet_bytes'].join(',')}}\n")
File.write("#{out}/identity.h",File.read("#{out}/identity.h").sub(identity,Digest::SHA256.hexdigest(identity+File.binread("#{out}/margin.bin"))[0,16]))
