#!/usr/bin/env ruby
# Complete stock commands and an independent expected receiver transcript.
require 'json'
output=ARGV.fetch(0)
Dir.mkdir(output) unless Dir.exist?(output)
polls=->(range) {range.flat_map { |n| [23,0,0x80,n] }}
packets=[polls.call(0...32),[23,0,0xa0,0x34,0x12,2,23,0,0xa0,0x34,0x12,0,0,16]+(0...4096).map{|n| (n*157+7)&255},polls.call(32...64)]
text=packets.each_with_index.map do |bytes,i|
  "packet#{i+1}:\n"+bytes.each_slice(16).map{|line| '    DB '+line.join(',')+"\n"}.join+"packet#{i+1}_end:\n"
end.join
File.write(File.join(output,'packets.inc'),text)
File.binwrite(File.join(output,'expected-tx.bin'),packets.flatten.pack('C*'))
File.binwrite(File.join(output,'expected-rx.bin'),(0...64).flat_map{|n| [0x80,1,n]}.pack('C*'))
File.write(File.join(output,'expected.json'),JSON.pretty_generate({packet_lengths:packets.map(&:length),tx_bytes:packets.flatten.size,rx_bytes:192})+"\n")
