require 'fileutils';require 'json';require 'zlib';require 'digest'
out=ARGV.fetch(0);FileUtils.mkdir_p(out)
cases=[5,20].flat_map{|hold|[64,96,112,120,124,126,127].flat_map{|t|3.times.map{[t,hold]}}}
payload=(0...4096).map{|n|((n*157+7)%254)+1}.pack('C*')
s="cases: DB "+cases.flatten.join(',')+"\nlabels:\n"
cases.each_with_index do |(t,h),i|
 text="Case #{format('%02d',i+1)}/42: threshold #{t}, RX service pause #{h} ms..."
 raise 'Case message too long' if text.size>61
 s+="label#{i}: DB \"#{text}\",13,10,0\n    DS #{64-text.size-3}\n"
end
s+="payload:\n"+payload.bytes.each_slice(24).map{|b|"    DB #{b.join(',')}\n"}.join+"    DB 0\npayload_end:\n"
File.write("#{out}/cases.inc",s)
File.write("#{out}/expected.json",JSON.pretty_generate(cases:cases,payload_bytes:payload.size,wire_bytes:payload.size+1,payload_crc32:Zlib.crc32(payload),payload_sha256:Digest::SHA256.hexdigest(payload),record_bytes:48)+"\n")
