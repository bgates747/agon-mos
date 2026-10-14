#!/usr/bin/env ruby
# Immutable off-device bundle; deployment is a separate explicit operation.
require 'json';require 'digest';require 'fileutils';require 'zlib'
root=File.expand_path('../..',__dir__);Dir.chdir(root)
out=File.expand_path(ARGV.fetch(0));abort 'Output already exists' if File.exist?(out)
b='build/uart0-suite';base='build/uart0-bench/console8-diagnostics-20261013'
receipts=%w[jit interp interactive].map{|e|JSON.parse(File.read("#{b}/evidence-#{e}/receipt.json"))}
receipts.each do |r|
 abort 'Suite qualification incomplete' unless r.fetch('returned_to_mos')
 {'test.bin'=>'sdcard/uart0/test.bin','bench/bench.bin'=>'sdcard/uart0/bench.bin','stress/stress.bin'=>'sdcard/uart0/stress.bin','api/app.bin'=>'sdcard/uart0/app.bin','api/short.bin'=>'sdcard/uart0/short.bin','margin.bin'=>'sdcard/uart0/margin.bin'}.each do |file,profilefile|
  pin=r.fetch('runtime_identities').find{|line|line.end_with?("  #{profilefile}")}&.split&.first
  abort "Changed since qualification: #{file}" unless pin==Digest::SHA256.file("#{b}/#{file}").hexdigest
 end
end
abort 'Missing flash cancellation checks' unless receipts.last.fetch('real_upstream_MOS_flash_cancelled') && receipts.last.fetch('real_upstream_VDP_flash_cancelled')
File.readlines("#{base}/SHA256SUMS",chomp:true).each{|line|hash,name=line.split('  ',2);abort 'Base package changed' unless File.basename(name)==name && Digest::SHA256.file("#{base}/#{name}").hexdigest==hash}
FileUtils.mkdir_p(out)
files={"#{b}/test.bin"=>'test.bin',"#{b}/bench/bench.bin"=>'bench.bin',"#{b}/stress/stress.bin"=>'stress.bin',"#{b}/api/app.bin"=>'app.bin',"#{b}/api/short.bin"=>'short.bin',"#{b}/checks.bin"=>'checks.bin',"#{b}/bench/expected.json"=>'bench.json',"#{b}/stress/expected.json"=>'stress.json','experiments/uart0-suite/suite.cfg'=>'suite.cfg','experiments/uart0-suite/readme.txt'=>'readme.txt','experiments/uart0-suite/CREDITS.txt'=>'CREDITS.txt','experiments/uart0-suite/README.md'=>'README.md','experiments/uart0-suite/analyze.rb'=>'analyze.rb','experiments/uart0-suite/results.json'=>'results.json','experiments/uart0-suite/observer-diagnosis.json'=>'observer-diagnosis.json','experiments/uart0-stress/capture.txt'=>'capture.txt','experiments/uart0-bench/analyze.rb'=>'bench-read.rb','experiments/uart0-stress/analyze.rb'=>'stress-read.rb'}
%w[mos-candidate.bin mos-candidate.map vdp-2.16.0.bin flash.bin MOS-LICENSE.txt VDP-LICENSE.txt FLASH-LICENSE.txt].each{|f|files["#{base}/#{f}"]=f}
%w[jit interp interactive].each{|e|files["#{b}/evidence-#{e}/receipt.json"]="check-#{e}.json"}
files.each{|src,dst|FileUtils.cp(src,"#{out}/#{dst}")}
FileUtils.cp("#{b}/margin.bin","#{out}/margin.bin")
FileUtils.cp('build/uart0-margin/expected.json',"#{out}/margin.json")
FileUtils.cp('experiments/uart0-margin/analyze.rb',"#{out}/margin-read.rb")
FileUtils.cp('experiments/uart0-suite/human-review-failure.json',"#{out}/human-review-failure.json")
FileUtils.cp('experiments/uart0-bench/analyze.rb',"#{out}/capture-analyze.rb")
FileUtils.cp('experiments/uart0-suite/firmware.txt',"#{out}/firmware.txt")
entries=Dir.children(out).sort.to_h{|n|[n,{bytes:File.size("#{out}/#{n}"),sha256:Digest::SHA256.file("#{out}/#{n}").hexdigest}]}
r=JSON.parse(File.read('experiments/uart0-suite/results.json'))
manifest={suite:true,deployment_path:'/test/mos-uart0',target:'Heber Agon Console8',automated_qualification_passed:true,human_review_passed:r.fetch('human_review_passed'),physical_qualification:false,report_version:1,build_id:r.fetch('build_id'),
 vdp:{version:'2.16.0',stock_release:true,exact_release_binary_emulator_qualified:false},files:entries}
File.write("#{out}/manifest.json",JSON.pretty_generate(manifest)+"\n")
File.write("#{out}/SHA256SUMS",(entries.keys+['manifest.json']).sort.map{|n|"#{Digest::SHA256.file("#{out}/#{n}").hexdigest}  #{n}\n"}.join)
puts "Prepared suite bundle #{out}; human emulator review #{r['human_review_passed'] ? 'passed' : 'pending'}"
