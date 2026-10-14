#!/usr/bin/env ruby
# All upstream trees are read-only. Build a pinned private diagnostic copy.
require 'fileutils';require 'json';require 'digest'
out=File.expand_path(ARGV.fetch(0));FileUtils.mkdir_p(out)
base='c7ac293d2aa81ddfa693390549bcd909069c8fc3'
firmware="#{out}/firmware";FileUtils.mkdir_p(firmware)
raise 'VDP source export failed' unless system("git -C /Agon/agon-vdp archive #{base} | tar -x -C '#{firmware}'")
FileUtils.mkdir_p("#{firmware}/lib")
libs='/Agon/agon-vdp/.pio/libdeps/esp32dev'
%w[CRC ESP32Time].each{|n|FileUtils.rm_rf("#{firmware}/lib/#{n}");FileUtils.cp_r("#{libs}/#{n}","#{firmware}/lib/#{n}")}
vdpgl='ac2dd5986daf496c43ae8e7fe41836274aec54a0';FileUtils.mkdir_p("#{firmware}/lib/vdp-gl")
raise 'VDP-GL export failed' unless system("git -C #{libs}/vdp-gl archive #{vdpgl} | tar -x -C '#{firmware}/lib/vdp-gl'")
ini=File.read("#{firmware}/platformio.ini")
ini=ini.sub(/lib_deps =.*?build_unflags =/m,"lib_deps =\nbuild_unflags =")
File.write("#{firmware}/platformio.ini",ini)
FileUtils.cp('experiments/uart0-margin/receiver.h',"#{firmware}/video/uart0_margin.h")
p="#{firmware}/video/vdu_stream_processor.h";s=File.read(p);s=s.sub('void sendGeneralPoll();','void sendGeneralPoll();\n        void uart0Margin();'.gsub('\\n',"\n"));File.write(p,s)
p="#{firmware}/video/vdu_sys.h";s=File.read(p);s=s.sub('#include "ymodem.h"',"#include \"ymodem.h\"\n#include \"uart0_margin.h\"");s=s.sub('case VDP_GP:',"case 0xE7: { uart0Margin(); } break;\n\t\tcase VDP_GP:");File.write(p,s)
p="#{firmware}/video/version.h";s=File.read(p).sub('"Bistromathics"','"UART0 CTS diagnostic"');File.write(p,s)
files=Dir.glob("#{firmware}/**/*").select{|p|File.file?(p)&&!p.include?('/.git/')}.sort
pins=files.to_h{|p|[p.delete_prefix(firmware+'/'),Digest::SHA256.file(p).hexdigest]}
File.write("#{out}/source.json",JSON.pretty_generate(vdp_commit:base,vdp_gl_commit:vdpgl,CRC:'1.0.4',ESP32Time:'2.0.6',platform:'espressif32@6.6.0',source_files_sha256:pins)+"\n")
