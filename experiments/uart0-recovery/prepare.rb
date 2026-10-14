#!/usr/bin/env ruby
require 'fileutils';require 'json';require 'digest'
b='build/uart0-recovery';FileUtils.mkdir_p(b)
raise 'Packet generation failed' unless system('ruby','experiments/uart0-bench/packets.rb',b)
inc=File.read("#{b}/packets.inc").sub(/packet:.*?packet_end:\n/m,'')
payload=(0...8192).map{|i|(i*157+7)&255};cmd=->(*v){[23,0,0xa0,0xf0,0x6a,*v]}
streams={bulk_packet:cmd.call(2)+cmd.call(0,0,32,*payload),small_packet:cmd.call(0,0,1,*payload.take(256)),duplex_packet:[23,0,0x80,16]+cmd.call(0,0,1,*payload.take(256)),case_clear:cmd.call(2),poll_ready:[23,0,0x80,0]}
streams.each{|n,v|inc+="#{n}:\n"+v.each_slice(24).map{|x|"    DB #{x.join(',')}\n"}.join+"#{n}_end:\n"}
inc=inc.sub(/duplex_packet:.*?duplex_packet_end:\n/m,'')
duplex=(0...32).flat_map{|i|[23,0,0x80,16+i]+cmd.call(0,0,1,*payload.take(256))}
inc+="duplex_packets:\n"+duplex.each_slice(24).map{|x|"    DB #{x.join(',')}\n"}.join+"duplex_packets_end:\n"
File.binwrite("#{b}/duplex-packets.bin",duplex.pack('C*'))
File.write("#{b}/packets.inc",inc)
File.binwrite("#{b}/bulk-packet.bin",streams[:bulk_packet].pack('C*'))
File.binwrite("#{b}/small-packet.bin",streams[:small_packet].pack('C*'))
base=File.read('experiments/uart0-bench/bench.asm')
clock=base[base.index('clock_read:')...base.index('progress_case:')]
print=base[base.index('print_hex_byte:')...base.index('reset_gp:')]
verify=base[base.index('verify_payload:')...base.index('api_missing:')]
verify=verify.sub("    ld a,2\n    ld (stage),a\n",'')
verify=verify.sub("    rst.lil 18h\nverify_more:","    rst.lil 18h\n    call checkpoint\nverify_more:")
File.write("#{b}/helpers.inc",clock+print+verify)
FileUtils.cp('experiments/uart0-recovery/recovery.asm',b)
File.write("#{b}/recovery.linkcmd",<<~LINK)
-FORMAT=OMF695,INTEL32
-map -maxhexlen=64 -quiet -warnoverlap -xref -warn=fatal
-sort NAME=ascending -debug -NOigcase
RANGE ROM $080000 : $08FFFF
ORDER UART_ENTRY
"recovery" = "recovery.obj"
LINK
File.write("#{b}/expected.json",JSON.pretty_generate(report_bytes:608,record_bytes:24,header_bytes:32,default_cases:6,extended_cases:24,
 expected_wire_bytes:[streams[:bulk_packet].size*64,streams[:duplex_packet].size*32,streams[:small_packet].size*32],
 final_buffer_bytes_checked_per_case:8192,bulk_intermediate_payloads_verified:false,payload_sha256:Digest::SHA256.hexdigest(payload.pack('C*')),
 fixed_report_name_offsets:[73,89,105],repeat_setting_offset:121,stock_VDP_commands_only:true)+"\n")
identity=File.read('build/uart0-suite/identity.h')
identifier=Digest::SHA256.hexdigest(File.binread('experiments/uart0-suite/src/main.c')+File.binread('experiments/uart0-recovery/recovery.asm'))[0,16]
File.write("#{b}/identity.h",identity.sub(/SUITE_BUILD_ID "[^"]+"/,"SUITE_BUILD_ID \"#{identifier}\""))
