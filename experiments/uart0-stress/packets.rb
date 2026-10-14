#!/usr/bin/env ruby
# Reuse the qualified byte comparator; generate only stock VDP commands.
require 'json'
require 'digest'
require 'fileutils'
out=ARGV.fetch(0)
# Run the benchmark generator in our own output directory, never mutate its build.
raise 'Comparator generator failed' unless system('ruby',File.expand_path('../uart0-bench/packets.rb',__dir__),out)
inc=File.read("#{out}/packets.inc")
inc=inc.sub(/packet:.*?packet_end:\n/m,'')
payload=(0...8192).map{|n|(n*157+7)&255}
u16=->(n){[n&255,n>>8]}
cmd=->(*b){[23,0,0xa0,*u16.call(0x6af0),*b]}
packets=[0,1,4,8].map do |pause|
  cmd.call(2)+[23,0,0xc3]*pause+payload.each_slice(256).with_index.flat_map do |chunk,i|
    cmd.call(0,*u16.call(chunk.size),*chunk)+[23,0,0x80,16+i]
  end
end
packets.each_with_index do |bytes,i|
 inc+="packet#{i}:\n"+bytes.each_slice(24).map{|b|"    DB #{b.join(',')}\n"}.join+"packet#{i}_end:\n"
 File.binwrite("#{out}/packet#{i}.bin",bytes.pack('C*'))
end
File.write("#{out}/packets.inc",inc)
File.delete("#{out}/expected-packet.bin")
File.write("#{out}/expected.json",JSON.pretty_generate(payload_bytes:8192,replies:32,
 tokens:(16...48).to_a,pause_frames:[0,1,4,8],packet_bytes:packets.map(&:size),
 packet_sha256:packets.map{|b|Digest::SHA256.hexdigest(b.pack('C*'))},record_bytes:16,
 check_sha256:Digest::SHA256.file("#{out}/checks.bin").hexdigest,
 payload_sha256:Digest::SHA256.hexdigest(payload.pack('C*')))+"\n")
