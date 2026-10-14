#!/usr/bin/env ruby
require 'csv';require 'json'
rows=CSV.read('build/uart0-ab/model.csv',headers:true).map{|r|r.to_h.transform_values.with_index{|v,i|i==1||i==2 ? v : Integer(v)}}
summary=rows.group_by{|r|[r['workload'],r['mode']]}.map do |(workload,mode),v|
 value=->(key){v.map{|x|x[key]}.sum.fdiv(v.size)}
 {workload:workload,mode:mode,repeats:v.size,service_model_cycles:value.call('service_model_cycles'),
 modeled_wire_bytes_per_second:value.call('wire_bytes')*18_432_000/value.call(workload=='paced' ? 'elapsed_model_cycles' : 'wire_completion_model_cycles'),
 useful_iterations:value.call('useful_iterations'),cts_reads:value.call('cts_reads'),late_feeds:v.sum{|x|x['late_feeds_over_128_cycles']}}
end
puts JSON.pretty_generate(scope:'Pinned instruction model with ideal UART: cycle/rate estimates only, not hardware measurements.',clock_hz_assumed:18_432_000,baud_assumed:1_152_000,uart_cycles_per_byte:160,summary:summary,rows:rows)
