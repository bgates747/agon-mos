#!/usr/bin/env ruby
# Offline report inspection only; never opens hardware.
require 'json'
module UARTStress
 def self.report(bytes,expected)
  need=->(ok,msg){raise ArgumentError,msg unless ok}
  need.call(bytes.bytesize==76 && bytes.byteslice(0,12)=="UART0ST1\x01\x00\x04\x00".b,'Incomplete or failed stress report')
  records=4.times.map do |n|
   b=bytes.byteslice(12+n*16,16).bytes
   u24=->(p){b[p]+(b[p+1]<<8)+(b[p+2]<<16)}
   need.call(b[0]==expected.fetch('pause_frames')[n],'Unexpected pause case/order')
   need.call(b[1]==32 && b[2]==32 && b[3].between?(1,32),'Missing replies or no observed overlap')
   need.call(u24.call(4)==expected.fetch('packet_bytes')[n],'Short accepted byte count')
   need.call(b[10]==0 && b[12]==0 && b[13]==47 && b[14]==0 && b[15]==0,'RX or reply-sequence error')
   {pause_frames:b[0],expected_replies:b[1],observed_replies:b[2],replies_while_busy:b[3],
    accepted:u24.call(4),raw_ticks:u24.call(7),rx_errors:b[10],modem_deltas:b[11],sequence_error:b[12],last_token:b[13]}
  end
  {records:records,receiver_bytes_compared:32768,ordered_reply_count:128,
   physical_cts_headroom_qualified:false,raw_ticks_are_uncalibrated:true}
 end
end
if $PROGRAM_NAME==__FILE__
 begin
  puts JSON.pretty_generate(UARTStress.report(File.binread(ARGV.fetch(0)),JSON.parse(File.read(ARGV.fetch(1)))))
 rescue ArgumentError,KeyError,IndexError=>e
  warn e.message
  exit 1
 end
end
