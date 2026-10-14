#!/usr/bin/env ruby
# Offline numbered-report reader. No device I/O or assumption about the RTC.
require 'json'
require 'digest'
if File.exist?(File.join(__dir__,'bench-read.rb'))
 require_relative 'bench-read';require_relative 'stress-read'
else
 require_relative '../uart0-bench/analyze';require_relative '../uart0-stress/analyze'
end
dir=File.expand_path(ARGV.fetch(0))
files=Dir.children(dir).to_h{|n|[n.downcase,File.join(dir,n)]}
read=->(n){File.binread(files.fetch(n.downcase))}
bench=JSON.parse(read.call('bench.json'));stress=JSON.parse(read.call('stress.json'))
index=read.call('runs.log').gsub("\r",'')
blocks=index.split(/(?=^UARTSUITE report_version=)/).reject(&:empty?)
runs=blocks.map do |log|
 header=log.lines.first
 match=header.match(/\AUARTSUITE report_version=(\d+) build=(\w+) run=(\d{4}) action=(\w+)/)
 raise 'Unrecognized run header' unless match && match[1]=='1'
 run=match[3];finish=log.match(/^END run=#{run} (PASS|FAIL|PENDING|SKIP)$/)
 tests=log.scan(/^TEST (\d+) (PASS|FAIL|PENDING|SKIP)$/).to_h
 pending_handoff=log.include?("FLASH_HANDOFF verification=PENDING")
 row={run:run,build:match[2],action:match[4],status:finish ? finish[1] : pending_handoff ? 'PENDING' : 'INCOMPLETE',tests:tests}
 row[:flash_return]=log.lines.find{|s|s.start_with?('FLASH_RETURN ')}&.strip
 row[:flash_skip]=log.lines.find{|s|s.start_with?('FLASH_SKIP ')}&.strip
 if tests['2']=='PASS' || tests['3']=='PASS'
  [['2','B',bench],['3','S',stress]].each do |test,prefix,expected|
   next unless tests[test]=='PASS'
   text=log.match(/^REPORT #{prefix}#{run}\.dat hex=([0-9A-F]+)$/)
   raise "Missing embedded report for #{test}/#{run}" unless text
   raw=[text[1]].pack('H*')
   raise 'Report file differs from journal' if files["#{prefix.downcase}#{run}.dat"] && read.call("#{prefix}#{run}.dat")!=raw
   row["test_#{test}"]=test=='2' ? UARTBench.report(raw,expected) : UARTStress.report(raw,expected)
  end
 end
 if tests['6']=='PASS'
  raise 'Incomplete integration witness' unless log.include?('INTEGRATION accepted=128/4110/128 GP=63 exit_session_closed=1 ADL0_return=1')
 end
if tests.key?('7') && tests['7']!='SKIP'
 name="H#{run}.dat"
 if files.key?(name.downcase)
  raw=read.call(name)
  if raw.bytesize==2028 && raw.getbyte(9)==3
   row[:receiver_margin]={status:'SKIP',reason:'Diagnostic VDP not installed'}
  else
   reader=File.join(__dir__,'margin-read.rb')
   require File.exist?(reader) ? reader : File.expand_path('../uart0-margin/analyze.rb',__dir__)
   physical=log.include?('MARGIN physical_target=1')
   row[:receiver_margin]=UARTMargin.report(raw,JSON.parse(read.call('margin.json')),physical:physical)
  end
 elsif tests['7']!='FAIL'
  raise "Missing receiver report #{name}"
 end
end
 row[:calibration]=log.lines.find{|s|s.start_with?('CALIBRATION ')}&.strip
 row
end
raise 'Duplicate run numbers in running log' unless runs.map{|r|r[:run]}.uniq.size==runs.size
puts JSON.pretty_generate(report_version:1,runs:runs,clock_independent_run_numbers:true,
 physical_cts_headroom_qualified:false,calibration_precision:'Manual key timing; external reference is operator supplied')
