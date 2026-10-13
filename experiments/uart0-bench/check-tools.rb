#!/usr/bin/env ruby
# Meaningful negative controls for the offline evidence readers.
require_relative 'analyze'
count=0
reject=->(&block){begin;block.call;rescue ArgumentError;count+=1;else;raise 'Malformed evidence was accepted';end}
expected={'work_checksum'=>1202774,'packet_bytes'=>8210,'work_iterations'=>131072}
u24=->(n){[n&255,(n>>8)&255,(n>>16)&255].pack('C*')}
report="UART0BN1\x01\x00\x08\x00".b
4.times{|p|2.times{|m|report<<[m,p].pack('CC')+u24.call(20-m*4)+u24.call(1202774)+u24.call(m*256)+u24.call(8210)+[0,1,0].pack('CCC')}}
UARTBench.report(report,expected)
reject.call{UARTBench.report(report[0...-1],expected)}
bad=report.dup;bad.setbyte(12+5,0);reject.call{UARTBench.report(bad,expected)}
bad=report.dup;bad.setbyte(12+11,0);reject.call{UARTBench.report(bad,expected)}
bad=report.dup;bad.setbyte(12+14,1);reject.call{UARTBench.report(bad,expected)}
bad=report.dup;bad.setbyte(12+17+1,1);reject.call{UARTBench.report(bad,expected)}
trace="kind,time_s,end_s,value\ncts,0,,1\ntx,0.000010,0.000018680555556,23\ncts,0.000014,,0\nrx,0.000020,0.000028680555556,128\ncts,0.000030,,1\n"
r=UARTBench.trace(trace);raise unless r[:cts_blocks][0][:completed_while_blocked]==1
reject.call{UARTBench.trace(trace.lines[0...-1].join)}
reject.call{UARTBench.trace(trace.sub('0.000018680555556','0.000019680555556'))}
reject.call{UARTBench.trace(trace.sub('rx,','framing-error,'))}
reject.call{UARTBench.trace(trace.sub('cts,0.000030,,1','cts,0.000013,,1'))}
dump=(0...131072).map{|i|(i+195)&255}.pack('C*')
dump[0,5]=[0xF3,0xED,0x7D,0x5B,0xC3].pack('C*')
UARTBench.rom('backup',dump)
UARTBench.rom('candidate',dump,dump[0,110611])
UARTBench.rom('restore',dump,dump)
reject.call{UARTBench.rom('backup',dump[0...-1])}
reject.call{UARTBench.rom('backup',"\xff".b*131072)}
reject.call{UARTBench.rom('restore',dump,dump.sub(/./m,"\xC4".b))}
reject.call{UARTBench.rom('candidate',dump)}
reject.call{UARTBench.rom('backup',dump.sub(/./m,"\xC4".b))}
puts "PASS offline report/trace/ROM readers and #{count} negative controls"
