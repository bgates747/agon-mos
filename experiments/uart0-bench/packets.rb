#!/usr/bin/env ruby
require 'json'
require 'digest'
require 'fileutils'
out=ARGV.fetch(0);FileUtils.mkdir_p(out)
base=0x6af0
u16=->(n){[n&255,n>>8]}
cmd=->(id,*bytes){[23,0,0xa0,*u16.call(id),*bytes]}
payload=(0...8192).map{|n|(n*157+7)&255}
clear=->(id){cmd.call(id,2)}
write=->(id,bytes){cmd.call(id,0,*u16.call(bytes.length),*bytes)}
# IDs: payload, mismatch-handler, failure-flag, GP-reply command, reference.
bad=cmd.call(base+2,5,2,0,0,1)
setup=(0...5).flat_map{|i|clear.call(base+i)}+
  write.call(base+1,bad)+write.call(base+2,[0])+write.call(base+3,[23,0,0x80,0])+write.call(base+4,payload)
reset=cmd.call(base+2,5,2,0,0,0)
reply=cmd.call(base+3,5,0x22,3,0,*u16.call(base+2),0,0)+cmd.call(base+3,1)
compare=->(offset,reference_offset){cmd.call(base+1,6,0x23,*u16.call(base),*u16.call(offset),*u16.call(base+4),*u16.call(reference_offset))}
# Buffer-to-buffer comparisons also work with VDP builds whose immediate-byte
# comparison leaves the high bytes of its signed source accumulator set.
# Each 15-byte command executes the mismatch handler if one stored byte differs.
checks=payload.each_index.flat_map{|offset|compare.call(offset,offset)}
streams={setup:setup, packet:clear.call(base)+write.call(base,payload)+[23,0,0x80,42],
  reset_flag:reset, reply:reply, mismatch_probe:clear.call(base)+write.call(base,[7])+reset+compare.call(0,1)+reply,
  match_probe:reset+compare.call(0,0)+reply, cleanup:(0...5).flat_map{|i|clear.call(base+i)}}
text=streams.map{|name,bytes| "#{name}:\n"+bytes.each_slice(24).map{|line|"    DB #{line.join(',')}\n"}.join+"#{name}_end:\n"}.join
File.write(File.join(out,'packets.inc'),text)
# The app reads/outputs complete 15-byte commands in 3,840-byte chunks.
File.binwrite(File.join(out,'checks.bin'),checks.pack('C*'))
File.binwrite(File.join(out,'expected-packet.bin'),streams[:packet].pack('C*'))
hl=0x123456;de=0x010203
131072.times do
  hl=(hl+de)&0xffffff
  de=(de&0xff0000)|(((((hl>>8)&255)^(hl&255))&255)<<8)|((de+1)&255)
end
File.write(File.join(out,'expected.json'),JSON.pretty_generate(payload_bytes:payload.size,packet_bytes:streams[:packet].size,
  work_iterations:131072,work_checksum:hl,final_seed:de,pairs:4,records:8,record_bytes:17,
  buffer_ids:(base...base+5).to_a,check_bytes:checks.size,check_commands:payload.size,
  check_sha256:Digest::SHA256.hexdigest(checks.pack('C*')),payload_sha256:Digest::SHA256.hexdigest(payload.pack('C*')))+"\n")
