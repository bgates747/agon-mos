#!/usr/bin/env ruby
require 'fileutils';require 'json';require 'zlib';require 'digest'
b='build/uart0-batching/native';FileUtils.mkdir_p(b)
cases=[5,20].flat_map{|hold|[1,2,4,8,16].map{|n|[n,hold]}}
payload=(0...4096).map{|n|((n*157+7)%254)+1}.pack('C*')
inc="cases: DB "+cases.flat_map{|n,h|[64,h]}.join(',')+"\nbatches: DB "+cases.map(&:first).join(',')+"\nlabels:\n"
cases.each_with_index do |(n,h),i|
 text="Case #{i+1}/10: CTS batch #{n}, RX pause #{h} ms, full CRC..."
 inc+="    DB \"#{text}\",13,10,0\n    DS #{64-text.size-3}\n"
end
# Deliberately noncontiguous spans and short descriptors exercise refill
# boundaries. Padding is never part of the borrowed payload or expected CRC.
inc+="payload:\n"+payload[0,15].bytes.map{|v|"    DB #{v}\n"}.join+"part1_end:\n    DS 11\npart2:\n"+payload[15,17].bytes.map{|v|"    DB #{v}\n"}.join+"part2_end:\n    DS 13\npart3:\n"+payload[32..].bytes.each_slice(24).map{|v|"    DB #{v.join(',')}\n"}.join+"    DB 0\npart3_end:\n"
expected_crc=[Zlib.crc32(payload)].pack('V').bytes
inc+="expected_crc: DB #{expected_crc.join(',')}\n"
File.write("#{b}/cases.inc",inc)
s=File.read('experiments/uart0-margin/host.asm')
a=s.index('    DB "MOS",0,1,"UTC1"');z=s.index('start:',a)
s=s[0...a]+"    DB \"MOS\",0,1,\"UBT1\"\nresult_name: DB \"batch.dat\",0\n    DS 6\nbaseline_name: DB \"batch-base.dat\",0\n    DS 1\nfailure_name: DB \"batch-fail.dat\",0\n    DS 1\n"+s[z..]
s=s.sub('    call discovery','    call discovery\n    ld (api_table),hl'.gsub('\\n',"\n"))
s=s.sub('    cp a,1\n    jp c,failed'.gsub('\\n',"\n"),'    cp a,2\n    jp c,failed'.gsub('\\n',"\n")).sub('    cp a,46','    cp a,54')
s=s.sub('    ld (tx_diag_take+1),hl',<<~'ASM'.rstrip)
    ld (tx_diag_take+1),hl
    ld hl,(api_table)
    ld de,7
    add hl,de
    bit 3,(hl)
    jp z,failed
    ld de,39
    add hl,de
    ld hl,(hl)
    ld (tx_set_cts_batch+1),hl
    ld hl,(api_table)
    ld de,49
    add hl,de
    ld hl,(hl)
    ld (tx_get_cts_batch+1),hl
ASM
s=s.sub('    call tx_reserve',<<~'ASM'.rstrip)
    ld a,(case_index)
    ld hl,batches
    ld de,0
    ld e,a
    add hl,de
    ld b,(hl)
    ld a,b
    ld (requested_batch),a
    call tx_set_cts_batch
    or a,a
    jp nz,failed
    call tx_get_cts_batch
    or a,a
    jp nz,failed
    ld a,(requested_batch)
    cp a,b
    jp nz,failed
    call tx_reserve
ASM
s=s.sub('    ld bc,payload_end-payload','    ld bc,part1_end-payload')
s=s.sub("wait_drain:\n",<<~'ASM')
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket2),hl
    ex de,hl
    ld hl,part2
    ld bc,part2_end-part2
    call tx_publish
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket3),hl
    ex de,hl
    ld hl,part3
    ld bc,part3_end-part3
    call tx_publish
    or a,a
    jp nz,failed
wait_drain:
ASM
s=s.sub('    ld de,payload_end-payload','    ld de,part1_end-payload')
s=s.sub('    call tx_close',<<~'ASM'.rstrip)
    ld de,(ticket2)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld de,part2_end-part2
    or a,a
    sbc hl,de
    jp nz,failed
    ld de,(ticket2)
    call tx_reap
    or a,a
    jp nz,failed
    ld de,(ticket3)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld de,part3_end-part3
    or a,a
    sbc hl,de
    jp nz,failed
    ld de,(ticket3)
    call tx_reap
    or a,a
    jp nz,failed
    call tx_close
ASM
# Validate every received byte via count/CRC, not the occupancy validity field
# (emulator FIFO/RTS measurements cannot be treated as physical evidence).
s=s.sub('    ld a,(case_index)\n    inc a'.gsub('\\n',"\n"),<<~'ASM'.rstrip)
    ld hl,(record_ptr)
    ld de,48
    or a,a
    sbc hl,de
    push hl
    pop ix
    ld hl,(ix+36)
    ld de,4096
    or a,a
    sbc hl,de
    jp nz,failed
    ld a,(ix+39)
    or a,a
    jp nz,failed
    ld hl,expected_crc
    ld de,40
    add ix,de
    ld b,4
crc_check:
    ld a,(hl)
    cp a,(ix+0)
    jp nz,failed
    inc hl
    inc ix
    djnz crc_check
    ld a,(ix+0)
    or a,a
    jp nz,failed
    ld a,(ix+1)
    cp a,1
    jp nz,failed
    ld a,(case_index)
    inc a
ASM
s=s.gsub('    cp a,42','    cp a,10').sub('    DB 42,0','    DB 10,0').sub('records: DS 42*48','records: DS 10*48')
s=s.sub('tx_diag_take: jp 0',"tx_diag_take: jp 0\ntx_set_cts_batch: jp 0\ntx_get_cts_batch: jp 0\nrequested_batch: DB 0\napi_table: DB 0,0,0\nticket2: DB 0,0,0\nticket3: DB 0,0,0")
s=s.sub('"URMHOST1",1','"UBTHOST1",1').sub('UART0 RECEIVER MARGIN EXPERIMENT','UART0 EXPERIMENTAL BATCH INTEGRITY')
s=s.sub('42 threshold/pause trials; allow up to two minutes.','10 size/pause trials; allow up to two minutes.').sub('Normal CTS stays enabled; failures at tight thresholds are evidence.','Stock threshold 64; noncontiguous sources; every payload CRC checked.')
s=s.sub('UART0 MARGIN TRANSPORT FAIL','UART0 BATCH TRANSPORT FAIL').sub('UART0 MARGIN DATA SAVED; inspect receiver CRC/FIFO evidence on host.','UART0 BATCH INTEGRITY PASS; every payload count/CRC verified.').sub('Saved data alone is not a CTS margin PASS.','Software integrity only; physical CTS margin remains unmeasured.')
File.write("#{b}/host.asm",s);FileUtils.cp('experiments/uart0-margin/host.linkcmd',b)
# Reuse the suite's already corrected one-outstanding-GP protocol and safe
# failure return rather than the historical standalone stress fixture.
inputs="#{b}/suite-inputs"
raise 'Suite input generation failed' unless system('ruby','experiments/uart0-suite/prepare.rb',inputs)
%w[packets.inc checks.bin packet0.bin packet1.bin packet2.bin packet3.bin].each do |name|
 FileUtils.cp("#{inputs}/stress/#{name}","#{b}/#{name}")
end
stress=File.read("#{inputs}/stress/stress.asm")
[1,2,4,8,16].each do |n|
 d="#{b}/stress#{n}";FileUtils.mkdir_p(d)
 t=stress.sub('    call discovery',"    call discovery\n    ld (api_table),hl").sub("    cp a,1\n    jp c,api_missing","    cp a,2\n    jp c,api_missing").sub('    cp a,46','    cp a,54')
 t=t.sub('    ld (tx_diag_take+1),hl',"    ld (tx_diag_take+1),hl\n    ld hl,(api_table)\n    ld de,46\n    add hl,de\n    ld hl,(hl)\n    ld (tx_set_cts_batch+1),hl")
 open="    call tx_open\n    or a,a\n    jp nz,failed\n"
 raise 'Missing open gate' unless t.scan(open).size==1
 t=t.sub(open,open+"    ld b,#{n}\n    call tx_set_cts_batch\n    or a,a\n    jp nz,failed\n")
 t=t.sub('tx_diag_take: jp 0',"tx_diag_take: jp 0\ntx_set_cts_batch: jp 0\napi_table: DB 0,0,0")
 {'result_name'=>"stress#{n}.dat",'baseline_name'=>"base#{n}.dat",'failure_name'=>"fail#{n}.dat"}.each do |label,name|
  pattern=/^#{label}: DB "[^"]+",0\n    DS \d+\n/
  raise "Missing fixed slot #{label}" unless t.match?(pattern)
  t=t.sub(pattern,"#{label}: DB \"#{name}\",0\n    DS #{15-name.size}\n")
 end
 t=t.sub('"UTC1"','"UBD1"').sub('UART0 PAUSE / FULL-DUPLEX TEST',"UART0 BATCH #{n} FULL-DUPLEX TEST")
 File.write("#{d}/stress.asm",t);FileUtils.cp("#{inputs}/stress/stress.linkcmd",d)
end
File.write("#{b}/expected.json",JSON.pretty_generate(cases:cases,payload_bytes:4096,payload_crc32:Zlib.crc32(payload),payload_sha256:Digest::SHA256.hexdigest(payload),report_bytes:492,source_lengths:[15,17,4065],sizes:[1,2,4,8,16],physical_qualification:false)+"\n")
