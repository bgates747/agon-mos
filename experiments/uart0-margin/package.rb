#!/usr/bin/env ruby
# Prepare off-device only. No SD access or flashing.
require 'json';require 'digest';require 'fileutils';require 'zlib'
root=File.expand_path('../..',__dir__);Dir.chdir(root)
out=File.expand_path(ARGV.fetch(0));abort 'Output exists' if File.exist?(out)
raise 'Base suite package failed' unless system('ruby','experiments/uart0-suite/package.rb',out)
files={'experiments/uart0-margin/CREDITS.txt'=>'margin-CREDITS.txt','build/uart0-margin/firmware/.pio/build/esp32dev/firmware.bin'=>'vdp-cts-diag.bin',
'experiments/uart0-margin/readme.txt'=>'readme.txt','experiments/uart0-margin/README.md'=>'margin-README.md',
'build/uart0-margin/source.json'=>'margin-source.json','build/uart0-margin/expected.json'=>'margin.json',
'experiments/uart0-margin/analyze.rb'=>'margin-read.rb','build/uart0-margin/firmware/LICENSE'=>'DIAGNOSTIC-VDP-LICENSE.txt'}
%w[jit interp jit-badcrc jit-noend jit-menu interp-menu].each do |e|
 p="build/uart0-margin/evidence-#{e}/receipt.json";r=JSON.parse(File.read(p))
 abort "Failed receiver qualification #{e}" unless r['returned_to_mos'] && (e.include?('badcrc')||e.include?('noend') ? r['control_rejected'] : r['verified_payloads']==42)
 pin=r.fetch('runtime_identities').find{|line|line.end_with?('  esp32-firmware.bin')}.split.first
 abort 'Firmware changed after qualification' unless pin==Digest::SHA256.file('build/uart0-margin/firmware/.pio/build/esp32dev/firmware.bin').hexdigest
 unless r['control']
  pin=r.fetch('runtime_identities').find{|line|line.end_with?('  sdcard/uart0/margin.bin')}.split.first
  abort 'Receiver fixture changed after qualification' unless pin==Digest::SHA256.file('build/uart0-margin/margin.bin').hexdigest
 end
 files[p]="margin-check-#{e}.json"
end
files.each{|src,dst|FileUtils.cp(src,File.join(out,dst))}
raise "Source archive failed" unless system("tar","--exclude=.pio","-czf",File.join(out,"diagnostic-sources.tar.gz"),"-C","build/uart0-margin","firmware")

cfg=File.read(File.join(out,'suite.cfg')).sub('vdp=vdp-2.16.0.bin','vdp=vdp-cts-diag.bin').sub('vdp_label=stock 2.16.0 (confirm installed version)','vdp_label=UART0 CTS diagnostic (confirm installed subtitle)')
File.write(File.join(out,'suite.cfg'),cfg)
manifest=JSON.parse(File.read(File.join(out,'manifest.json')))
manifest['receiver_margin_experiment']=true;manifest['human_review_passed']=false
manifest['vdp']={version:'2.16.0',stock_release:false,diagnostic_file:'vdp-cts-diag.bin',stock_restore:'vdp-2.16.0.bin',source_commit:'c7ac293d2aa81ddfa693390549bcd909069c8fc3',crc32:'%08X'%Zlib.crc32(File.binread(File.join(out,'vdp-cts-diag.bin')))}
manifest['files']=Dir.children(out).reject{|n|%w[manifest.json SHA256SUMS].include?(n)}.sort.to_h{|n|[n,{bytes:File.size(File.join(out,n)),sha256:Digest::SHA256.file(File.join(out,n)).hexdigest}]}
File.write(File.join(out,'manifest.json'),JSON.pretty_generate(manifest)+"\n")
File.write(File.join(out,'SHA256SUMS'),(manifest['files'].keys+['manifest.json']).sort.map{|n|"#{Digest::SHA256.file(File.join(out,n)).hexdigest}  #{n}\n"}.join)
puts "Diagnostic bundle prepared off-device: #{out}; manual flashing and human review pending."
