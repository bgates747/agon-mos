#!/usr/bin/env ruby
require 'fileutils';require 'json'
root=File.expand_path('../..',__dir__);Dir.chdir(root);out='build/uart0-ab/native';FileUtils.mkdir_p(out)
modes=%w[default grouped chunk otirx]
modes.each do |mode|
 s=File.read("build/uart0-ab/#{mode}/uart0_tx.inc")
 names=s.scan(/XDEF\s+([^\n]+)/).flat_map{|v|v.first.split(',').map(&:strip)}.uniq
 names += s.scan(/^\s+API\s+(\w+),/).flatten
 names.uniq!
 names.delete('tx_rx_sink')
 names.sort_by{|n|-n.length}.each{|n|s=s.gsub(/\b#{Regexp.escape(n)}\b/,"#{mode}_#{n}")}
 s=s.gsub('UART_DRIVER',"UART_DRIVER_#{mode}")
 File.write("#{out}/#{mode}.asm","UART0_PRODUCTION EQU 0\n"+s+"\n    END\n")
end
FileUtils.cp('experiments/uart0-ab/native.asm',"#{out}/app.asm")
FileUtils.cp('experiments/uart0-async/fixture.asm',"#{out}/fixture.asm")
# Fixture only supplies RX capture; its callback-test pointer uses default core.
p="#{out}/fixture.asm";File.write(p,File.read(p).gsub(/\btx_status\b/,'default_tx_status'))
File.write("#{out}/app.linkcmd",<<~LINK)
-FORMAT=OMF695,INTEL32
-map -maxhexlen=64 -quiet -warnoverlap -xref -warn=fatal
-sort NAME=ascending -debug -NOigcase
RANGE ROM $040000 : $04FFFF
ORDER UART_ENTRY, #{modes.map{|m|"UART_DRIVER_#{m}"}.join(', ')}, UART_FIXTURE
"app" = "app.obj", #{modes.map{|m|"\"#{m}.obj\""}.join(', ')}, "fixture.obj"
LINK
File.write("#{out}/native-table.inc","driver_table:\n"+modes.map{|m|"    XREF #{%w[tx_open tx_reserve tx_publish tx_poll_drain tx_reap tx_close tx_isr tx_rx_errors].map{|f|"#{m}_#{f}"}.join(',')}\n    DW24 #{%w[tx_open tx_reserve tx_publish tx_poll_drain tx_reap tx_close tx_isr tx_rx_errors].map{|f|"#{m}_#{f}"}.join(',')}\n"}.join)
base=0x7010;u16=->(n){[n&255,n>>8]};cmd=->(id,*b){[23,0,0xa0,*u16.call(id),*b]}
clear=->(id){cmd.call(id,2)};write=->(id,data){cmd.call(id,0,*u16.call(data.size),*data)}
data=(0...16370).map{|n|(n*157+7)&255};bad=cmd.call(base+2,5,2,0,0,1)
setup=(0...5).flat_map{|i|clear.call(base+i)}+write.call(base+1,bad)+write.call(base+2,[0])+write.call(base+3,[23,0,0x80,0])+write.call(base+4,data.take(735))
reset=cmd.call(base+2,5,2,0,0,0);reply=cmd.call(base+3,5,0x22,3,0,*u16.call(base+2),0,0)+cmd.call(base+3,1)
compare=->(a,b){cmd.call(base+1,6,0x23,*u16.call(base),*u16.call(a),*u16.call(base+4),*u16.call(b))}
streams={setup:setup,mismatch_probe:clear.call(base)+write.call(base,[7])+reset+compare.call(0,1)+reply,match_probe:reset+compare.call(0,0)+reply,
 bulk_packet:clear.call(base)+write.call(base,data),pace_packet:clear.call(base)+write.call(base,data.take(735)),
 verify_reset:reset,verify_data:(0...735).flat_map{|i|compare.call(i,i)},verify_reply:reply,cleanup:(0...5).flat_map{|i|clear.call(base+i)}}
File.write("#{out}/native-packets.inc",streams.map{|n,b|"#{n}:\n"+b.each_slice(24).map{|v|"    DB #{v.join(',')}\n"}.join+"#{n}_end:\n"}.join)
File.binwrite("#{out}/bulk-packet.bin",streams[:bulk_packet].pack('C*'));File.binwrite("#{out}/pace-packet.bin",streams[:pace_packet].pack('C*'))
File.write("#{out}/expected.json",JSON.pretty_generate(bulk_bytes:streams[:bulk_packet].size*3,pace_bytes:streams[:pace_packet].size*60,phases:30,receiver_checked_bytes_per_phase:735,receiver_bulk_full_payload_verified:false,scope:'Isolated candidate kernels; fixed stock VDP command workload; not a Jukebox adaptation or physical cycle measurement.')+"\n")
