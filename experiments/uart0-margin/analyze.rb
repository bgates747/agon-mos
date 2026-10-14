#!/usr/bin/env ruby
# Offline only. Emulator counters never qualify a physical receiver.
require 'json';require 'zlib'
module UARTMargin
 def self.report(bytes,expected,physical:false)
  raise 'Incomplete diagnostic report' unless bytes.size==2028 && bytes[0,12]=="URMHOST1\x01\x00\x2a\x00".b
  rows=expected.fetch('cases').each_with_index.map do |(threshold,hold),n|
   b=bytes[12+n*48,48].bytes;u32=->(p){b[p,4].pack('C*').unpack1('V')}
   raise "Wrong receiver identity/case #{n}" unless b[0,4].pack('C*')=='URM1' && b[4]==1 && b[5]==threshold && b[6]==hold
   count=u32.call(36);crc=u32.call(40);err=u32.call(24)
   crc_ok=count==expected.fetch('payload_bytes') && crc==expected.fetch('payload_crc32')
   framing=err&~16
   valid=b[46]==1 && b[45]==1 && b[47]==0 && b[44]==0 && u32.call(12)==0 && u32.call(8)==0 && b[7]==0 && u32.call(18)==0 && b[16]==threshold && b[17]==1 && b[22].between?(threshold+1,128) && b[23]==b[22] && u32.call(32)>=200 && u32.call(28)>=hold*1000
   outcome=if b[44]!=0 || b[47]!=0 then 'PROTOCOL_ERROR'
    elsif framing!=0 then 'RX_SIGNAL_ERROR'
    elsif !crc_ok && (err&16)==0 then 'UNEXPLAINED_DATA_FAILURE'
    elsif !valid then 'MEASUREMENT_INVALID'
    elsif err&16!=0 then 'FIFO_OVERFLOW_BOUNDARY'
    elsif crc_ok then 'PASS'
    else 'UNEXPLAINED_DATA_FAILURE' end
   {case:n+1,threshold:threshold,hold_ms:hold,peak_fifo:b[22],settled_fifo:b[23],hold_us:u32.call(28),settled_us:u32.call(32),
    rx_error_bits:err,received_bytes:count,crc32:'%08X'%crc,receiver_bytes_and_crc_match:crc_ok,restore_verified:b[45]==1,hardware_conditions_valid:valid,
    protocol_flags:b[44],host_rx_errors:b[47],outcome:outcome,
    inferred_bytes_after_threshold: valid && err==0 ? b[23]-(threshold+1) : nil,
    observed_FIFO_space_remaining:valid && err==0 ? 128-b[23] : nil}
  end
  baseline=rows.select{|r|r[:threshold]==64};boundary=rows.select{|r|r[:outcome]=='FIFO_OVERFLOW_BOUNDARY'}
  {rows:rows,protocol_payloads_verified:rows.count{|r|r[:receiver_bytes_and_crc_match]},
   baseline_64_passed:physical && baseline.all?{|r|r[:outcome]=='PASS'},
   observed_overflow_thresholds:boundary.map{|r|r[:threshold]}.uniq,
   minimum_observed_stock_FIFO_space:physical && baseline.all?{|r|r[:outcome]=='PASS'} ? baseline.map{|r|r[:observed_FIFO_space_remaining]}.min : nil,
   physical_measurement:physical,electrical_CTS_edge_timing_measured:false,
   physical_margin_qualified:false,
   scope:physical ? 'Empirical receiver occupancy/threshold operating evidence only; review validity, repeats and controls before qualification.' : 'Emulator protocol exercise only; FIFO/RTS counters do not qualify physical margin.'}
 end
end
if $PROGRAM_NAME==__FILE__
 puts JSON.pretty_generate(UARTMargin.report(File.binread(ARGV.fetch(0)),JSON.parse(File.read(ARGV.fetch(1))),physical:ARGV.include?('--physical')))
end
