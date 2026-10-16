require 'fileutils';require 'json';require 'zlib';require 'digest'
b='build/uart0-race';FileUtils.mkdir_p(b)
payload=(0...4096).map{|n|((n*157+7)%254)+1}.pack('C*')
s="cases: DB 0,0,1,0\nlabels:\n"
['Case 1/2: no timing trigger; normal receiver recovery...',
 'Case 2/2: widen ISR window; capture state before rescue...'].each_with_index do |text,i|
 raise if text.size>61
 s+="label#{i}: DB \"#{text}\",13,10,0\n    DS #{64-text.size-3}\n"
end
s+="payload:\n"+payload.bytes.each_slice(24).map{|x|"    DB #{x.join(',')}\n"}.join+"    DB 0\npayload_end:\n"
File.write("#{b}/cases.inc",s)
FileUtils.cp('experiments/uart0-race/host.asm',"#{b}/host.asm")
FileUtils.cp('experiments/uart0-margin/host.linkcmd',"#{b}/host.linkcmd")
File.write("#{b}/expected.json",JSON.pretty_generate(record_bytes:160,report_bytes:332,payload_bytes:4096,wire_bytes:4097,payload_crc32:Zlib.crc32(payload),payload_sha256:Digest::SHA256.hexdigest(payload),report_name_offsets:[73,89,105,121])+"\n")
id=Digest::SHA256.hexdigest(File.binread('experiments/uart0-suite/src/main.c')+File.binread('experiments/uart0-suite/src/uart.src')+File.binread('experiments/uart0-race/host.asm'))[0,16]
File.write("#{b}/identity.h",File.read('build/uart0-suite/identity.h').sub(/SUITE_BUILD_ID "[^"]+"/,"SUITE_BUILD_ID \"#{id}\""))
