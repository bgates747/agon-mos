#!/usr/bin/env ruby
# Creates a NEW off-device directory; never deploys to removable media.
require 'json'
require 'fileutils'
require 'digest'
require 'zlib'
root=File.expand_path('../..',__dir__);Dir.chdir(root)
build='build/uart0-bench'
out=File.expand_path(ARGV.fetch(0))
abort 'Output already exists; choose a fresh package directory' if File.exist?(out)
accepted=JSON.parse(File.read('experiments/uart0-mos/results.json'))
fixture=JSON.parse(File.read('experiments/uart0-bench/results.json'))
rom=File.binread("#{build}/MOS.bin")
abort 'ROM differs from accepted candidate' unless Digest::SHA256.hexdigest(rom)==accepted.fetch('rom_sha256')
flash=File.binread("#{build}/upstream/flash.bin")
abort 'Flash utility pin mismatch' unless Digest::SHA256.hexdigest(flash)=='480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57'
abort 'Flash license pin mismatch' unless Digest::SHA256.file("#{build}/upstream/flash-LICENSE.txt").hexdigest=='7f5a596f6c9f72cb9d38b53cdc33b84bfdc068baa705ff8b8f3faab41e9eff99'
vdp=File.binread("#{build}/upstream/vdp-2.16.0.bin")
abort 'Stock VDP release pin mismatch' unless Digest::SHA256.hexdigest(vdp)=='b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f'
abort 'VDP license pin mismatch' unless Digest::SHA256.file("#{build}/upstream/VDP-LICENSE.txt").hexdigest=='fae2cacdc47dc5ed8efbd052201834108167942f0b524b8238327e9fbe13fd25'
receipts=%w[jit interp].map{|e|JSON.parse(File.read("#{build}/evidence-#{e}/receipt.json"))}
receipts.each do |r|
 abort 'Unqualified fixture' unless r.fetch('returned_to_mos') && r.fetch('receiver_bytes_compared')==65536 && r.fetch('corruption_negative_control_passed')
 {'bench.bin'=>'sdcard/uart0/bench.bin','checks.bin'=>'sdcard/uart0/checks.bin','MOS.map'=>'mos_platform.map'}.each do |file,profile_file|
  identity=r.fetch('runtime_identities').find{|x|x.end_with?("  #{profile_file}")}
  abort "#{file} changed since qualification" unless identity && identity.split.first==Digest::SHA256.file("#{build}/#{file}").hexdigest
 end
end
FileUtils.mkdir_p(out)
files={"#{build}/MOS.bin"=>'mos-candidate.bin',"#{build}/MOS.map"=>'mos-candidate.map',"#{build}/bench.bin"=>'bench.bin',"#{build}/checks.bin"=>'checks.bin',"#{build}/expected.json"=>'expected.json',"#{build}/expected-packet.bin"=>'expected-packet.bin',"#{build}/upstream/flash.bin"=>'flash.bin',"#{build}/upstream/flash-LICENSE.txt"=>'FLASH-LICENSE.txt','LICENSE'=>'MOS-LICENSE.txt','experiments/uart0-bench/README.md'=>'README.md','experiments/uart0-bench/analyze.rb'=>'analyze.rb','experiments/uart0-bench/results.json'=>'results.json'}
files.merge!("#{build}/upstream/vdp-2.16.0.bin"=>'vdp-2.16.0.bin',"#{build}/upstream/VDP-LICENSE.txt"=>'VDP-LICENSE.txt','experiments/uart0-bench/readme.txt'=>'readme.txt')
%w[jit interp].each{|e|files["#{build}/evidence-#{e}/receipt.json"]="headless-#{e}.json"}
files.each{|source,name|FileUtils.cp(source,"#{out}/#{name}")}
manifest={target:'Heber Agon Console8',deployment_path:'/test/mos-uart0',physical_qualification:false,
 candidate_bytes:rom.size,candidate_sha256:Digest::SHA256.hexdigest(rom),candidate_crc32:'%08X'%Zlib.crc32(rom),
 source_commit:`git rev-parse HEAD`.strip,fixture_status:fixture.fetch('human_review_passed') ? 'TX-011/TX-012 accepted; physical qualification pending' : 'Pending TX-012 human emulator review',
 packaging_sources:%w[package.rb readme.txt deploy.py].to_h{|name|[name,Digest::SHA256.file("experiments/uart0-bench/#{name}").hexdigest]},
 vdp:{version:'2.16.0',stock_release:true,bytes:vdp.size,crc32:'%08X'%Zlib.crc32(vdp),sha256:Digest::SHA256.hexdigest(vdp),source_commit:'c7ac293d2aa81ddfa693390549bcd909069c8fc3',url:'https://github.com/AgonPlatform/agon-vdp/releases/download/v2.16.0/firmware.bin',exact_release_binary_emulator_qualified:false},
 flash:{version:'v1.9',source_commit:'e670b5bd910dfe372c29aa9e896e6c24cc8530ec',url:'https://github.com/AgonPlatform/agon-flash/releases/download/v1.9/flash.bin'},
 files:files.values.to_h{|name|[name,{bytes:File.size("#{out}/#{name}"),sha256:Digest::SHA256.file("#{out}/#{name}").hexdigest} ]}}
File.write("#{out}/manifest.json",JSON.pretty_generate(manifest)+"\n")
File.write("#{out}/SHA256SUMS",(files.values+['manifest.json']).sort.map{|name|"#{Digest::SHA256.file("#{out}/#{name}").hexdigest}  #{name}\n"}.join)
puts "Prepared off-device package #{out} (#{manifest[:candidate_sha256]})"
