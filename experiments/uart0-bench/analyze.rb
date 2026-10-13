#!/usr/bin/env ruby
# Offline evidence only. Never opens a device or writes firmware.
require 'json'
require 'csv'
require 'digest'
require 'zlib'
module UARTBench
  def self.need(ok, message)
    raise ArgumentError, message unless ok
  end
  def self.report(bytes, expected)
    need(bytes.bytesize == 148 && bytes[0,12] == "UART0BN1\x01\x00\x08\x00".b, 'Incomplete or failed bench report')
    rows = 8.times.map do |n|
      b=bytes.byteslice(12+n*17,17).bytes
      u24=->(p){b[p]+(b[p+1]<<8)+(b[p+2]<<16)}
      r={mode:b[0],pair:b[1],raw_ticks:u24.call(2),checksum:u24.call(5),overlap_iterations:u24.call(8),accepted:u24.call(11),rx_errors:b[14],modem_deltas:b[15],receiver_result:b[16]}
      need(r[:checksum]==expected.fetch('work_checksum'), 'Fixed work checksum mismatch')
      need(r[:accepted]==expected.fetch('packet_bytes'), 'Short accepted byte count')
      need(r[:rx_errors]==0 && r[:receiver_result]==0, 'Receiver/UART error')
      need(r[:mode]==0 ? r[:overlap_iterations]==0 : r[:overlap_iterations].between?(1,expected.fetch('work_iterations')), 'Invalid overlap work count')
      r
    end
    need(rows.map{|r|[r[:pair],r[:mode]]}.sort == (0...4).flat_map{|p|[[p,0],[p,1]]}, 'Missing or duplicate paired case')
    pairs=(0...4).map do |p|
      a=rows.find{|r|r[:pair]==p && r[:mode]==0};b=rows.find{|r|r[:pair]==p && r[:mode]==1}
      {pair:p,blocking_ticks:a[:raw_ticks],async_ticks:b[:raw_ticks],ticks_saved:a[:raw_ticks]-b[:raw_ticks],overlap_iterations:b[:overlap_iterations]}
    end
    {records:rows,pairs:pairs,raw_ticks_are_uncalibrated:true,physical_qualification_established:false}
  end
  # Normalized logic-analyzer export: one row per decoded 8N1 byte or CTS edge.
  # time_s is byte start; end_s is stop-bit end. CTS ready is logical, active-low.
  def self.trace(csv)
    rows=CSV.parse(csv,headers:true)
    need(rows.headers==%w[kind time_s end_s value], 'Expected CSV header: kind,time_s,end_s,value')
    last=-Float::INFINITY; ends={}; bytes=[];edges=[]
    rows.each do |r|
      t=Float(r['time_s']);need(t.finite? && t>=0 && t>=last,'Unordered or invalid trace time');last=t
      case r['kind']
      when 'cts'
        need(%w[0 1].include?(r['value']) && r['end_s'].to_s.empty?, 'Invalid CTS edge')
        ready=r['value']=='1';need(edges.empty? || edges.last[1]!=ready,'Duplicate CTS level');edges<<[t,ready]
      when 'tx','rx'
        e=Float(r['end_s']);v=Integer(r['value'],10)
        need(e.finite? && e>t && v.between?(0,255),'Invalid decoded byte')
        need(((e-t)*1_152_000/10-1).abs<=0.02,'Byte duration differs from 1.152 Mbaud 8N1 by more than 2%')
        need(!ends.key?(r['kind']) || t>=ends[r['kind']]-1e-12,'Overlapping byte frames')
        ends[r['kind']]=e;bytes<<[r['kind'],t,e,v]
      else
        raise ArgumentError,'Unknown trace kind or framing-error row'
      end
    end
    need(edges.size>=3 && edges.first[1] && edges.last[1], 'Need initial ready, complete blocked interval and final ready')
    need(!bytes.empty? && bytes.all?{|b|b[1]>=edges.first[0] && b[2]<=edges.last[0]},'CTS capture does not bracket all byte frames')
    blocked=edges.each_cons(2).filter_map do |a,b|
      next if a[1]
      tx=bytes.select{|x|x[0]=='tx'}
      during=tx.select{|x|x[2]>a[0] && x[2]<=b[0]}
      {blocked_at_s:a[0],ready_at_s:b[0],completed_while_blocked:during.size,
       started_while_blocked:tx.count{|x|x[1]>=a[0] && x[1]<b[0]},
       tail_seconds: during.empty? ? 0 : during.last[2]-a[0]}
    end
    need(!blocked.empty?,'No CTS blockage captured')
    {tx_bytes:bytes.count{|x|x[0]=='tx'},rx_bytes:bytes.count{|x|x[0]=='rx'},cts_blocks:blocked,
      headroom_qualification_established:false,reason:'Observed wire tail needs an independently established receiver reserve and controlled stop/restart evidence.'}
  end
  def self.rom(kind, dump, reference=nil)
    need(kind=='backup' || reference, 'Candidate/restore verification needs a reference file')
    need(dump.bytesize==131072,'MOS dump must be exactly 128 KiB')
    need(dump.bytes.uniq.size>16 && dump.start_with?([0xF3,0xED,0x7D,0x5B,0xC3].pack('C*')), 'MOS dump lacks the startup header required by agon-flash')
    if reference
      need(kind=='candidate' ? dump.start_with?(reference) : dump==reference, 'MOS readback differs from reference')
    end
    {kind:kind,bytes:dump.bytesize,sha256:Digest::SHA256.hexdigest(dump),crc32:'%08X'%Zlib.crc32(dump),
      comparison: reference ? (kind=='candidate' ? 'Exact candidate prefix; unused flash tail not asserted' : 'Exact full installed-MOS restore') : 'Inventory only; inspect provenance before accepting backup'}
  end
end
if $PROGRAM_NAME==__FILE__
  begin
    mode=ARGV.shift
    result=case mode
    when 'report' then UARTBench.report(File.binread(ARGV.fetch(0)),JSON.parse(File.read(ARGV.fetch(1))))
    when 'trace' then UARTBench.trace(File.read(ARGV.fetch(0)))
    when 'backup','candidate','restore' then UARTBench.rom(mode,File.binread(ARGV.fetch(0)),ARGV[1] && File.binread(ARGV[1]))
    else raise ArgumentError,'Usage: analyze.rb report bench.dat expected.json | trace capture.csv | backup dump.bin | candidate dump.bin MOS.bin | restore dump.bin original.bin'
    end
    puts JSON.pretty_generate(result)
  rescue ArgumentError,KeyError => e
    warn e.message
    exit 1
  end
end
