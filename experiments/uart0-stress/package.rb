#!/usr/bin/env ruby
# Off-device packaging only. Never writes removable media or flashes firmware.
require 'json'
require 'digest'
require 'fileutils'
root=File.expand_path('../..',__dir__)
Dir.chdir(root)
out=File.expand_path(ARGV.fetch(0))
abort 'Package output already exists; choose a fresh directory' if File.exist?(out)
build='build/uart0-stress'
base='build/uart0-bench/console8-diagnostics-20261013'
File.readlines("#{base}/SHA256SUMS",chomp:true).each do |line|
 hash,name=line.split('  ',2)
 abort 'Unsafe base package filename' unless File.basename(name)==name
 abort "Base package pin mismatch: #{name}" unless Digest::SHA256.file("#{base}/#{name}").hexdigest==hash
end
accepted=JSON.parse(File.read('experiments/uart0-mos/results.json')).fetch('rom_sha256')
abort 'MOS differs from accepted candidate' unless Digest::SHA256.file("#{base}/mos-candidate.bin").hexdigest==accepted
abort 'Build MOS differs' unless Digest::SHA256.file("#{build}/MOS.bin").hexdigest==accepted
require_relative 'analyze'
expected=JSON.parse(File.read("#{build}/expected.json"))
%w[jit interp].each do |e|
 receipt=JSON.parse(File.read("#{build}/evidence-#{e}/receipt.json"))
 UARTStress.report(File.binread("#{build}/evidence-#{e}/stress.dat"),expected)
 abort 'Incomplete qualification' unless receipt.fetch('returned_to_mos') && receipt.fetch('receiver_bytes_compared')==32768
 {'test.bin'=>'sdcard/uart0/test.bin','checks.bin'=>'sdcard/uart0/checks.bin','MOS.map'=>'mos_platform.map','MOS.bin'=>'mos_platform.bin'}.each do |file,profilefile|
  hash=receipt.fetch('runtime_identities').find{|line|line.end_with?("  #{profilefile}")}&.split&.first
  abort "Changed after qualification: #{file}" unless hash==Digest::SHA256.file("#{build}/#{file}").hexdigest
 end
end
%w[sequence payload].each do |control|
 abort "Unproven negative control: #{control}" unless JSON.parse(File.read("#{build}/evidence-control-#{control}/receipt.json")).fetch('rejected')
end
FileUtils.mkdir_p(out)
%w[mos-candidate.bin mos-candidate.map vdp-2.16.0.bin flash.bin MOS-LICENSE.txt VDP-LICENSE.txt FLASH-LICENSE.txt].each{|f|FileUtils.cp("#{base}/#{f}","#{out}/#{f}")}
%w[test.bin checks.bin expected.json].each{|f|FileUtils.cp("#{build}/#{f}","#{out}/#{f}")}
%w[readme.txt README.md capture.txt analyze.rb results.json].each{|f|FileUtils.cp("experiments/uart0-stress/#{f}","#{out}/#{f}")}
FileUtils.cp('experiments/uart0-bench/analyze.rb',"#{out}/capture-analyze.rb")
# Extract only firmware/recovery sections from the validated prior runbook.
previous=File.read('experiments/uart0-bench/readme.txt')
firmware="FIRMWARE REFERENCE - SKIP IF PASSING CANDIDATE IS STILL INSTALLED\n\n"+
 previous[previous.index('BEFORE FLASHING')...previous.index('RUN THE TEST')]+"\n"+
 previous[previous.index('RESTORE THE ORIGINAL MOS WHEN FINISHED')...previous.index('RETURN RESULTS TO ORYX')]
File.write("#{out}/firmware.txt",firmware.gsub('/test/mos-uart0','/test/mos-uart0'))
%w[jit interp].each{|e|FileUtils.cp("#{build}/evidence-#{e}/receipt.json","#{out}/headless-#{e}.json")}
%w[sequence payload].each{|e|FileUtils.cp("#{build}/evidence-control-#{e}/receipt.json","#{out}/negative-#{e}.json")}
files=Dir.children(out).sort.to_h{|f|[f,{bytes:File.size("#{out}/#{f}"),sha256:Digest::SHA256.file("#{out}/#{f}").hexdigest}]}
reviewed=JSON.parse(File.read('experiments/uart0-stress/results.json')).fetch('human_review_passed')
manifest={target:'Heber Agon Console8',deployment_path:'/test/mos-uart0',human_review_passed:reviewed,
 physical_qualification:false,physical_cts_headroom_qualified:false,candidate_sha256:accepted,candidate_crc32:'7E66FD09',
 vdp:{version:'2.16.0',stock_release:true,exact_release_binary_emulator_qualified:false},
 source_commit:IO.popen(%w[git rev-parse HEAD],&:read).strip,working_tree_uncommitted:true,files:files}
File.write("#{out}/manifest.json",JSON.pretty_generate(manifest)+"\n")
File.write("#{out}/SHA256SUMS",(files.keys+['manifest.json']).sort.map{|f|"#{Digest::SHA256.file("#{out}/#{f}").hexdigest}  #{f}\n"}.join)
puts "Prepared off-device package #{out}; human emulator review #{reviewed ? 'passed' : 'pending'}"
