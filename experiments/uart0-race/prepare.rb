#!/usr/bin/env ruby
# Private pinned source exports; never modify upstream or installed SDK libraries.
require 'fileutils';require 'digest';require 'json';require 'open3'
out=File.expand_path('build/uart0-race');fw="#{out}/firmware";FileUtils.mkdir_p(fw)
base='c7ac293d2aa81ddfa693390549bcd909069c8fc3'
archive,status=Open3.capture2('git','-C','/Agon/agon-vdp','archive',base);raise 'VDP export failed' unless status.success?
IO.popen(['tar','-x','-C',fw],'wb'){|p|p.write(archive)};raise 'Extraction failed' unless $?.success?
libs='/Agon/agon-vdp/.pio/libdeps/esp32dev';FileUtils.mkdir_p("#{fw}/lib")
%w[CRC ESP32Time].each{|n|FileUtils.cp_r("#{libs}/#{n}","#{fw}/lib/") unless File.exist?("#{fw}/lib/#{n}")}
FileUtils.mkdir_p("#{fw}/lib/vdp-gl")
gl='ac2dd5986daf496c43ae8e7fe41836274aec54a0'
data,status=Open3.capture2('git','-C',"#{libs}/vdp-gl",'archive',gl);raise unless status.success?
IO.popen(['tar','-x','-C',"#{fw}/lib/vdp-gl"],'wb'){|p|p.write(data)};raise unless $?.success?
ini=File.read("#{fw}/platformio.ini").sub(/lib_deps =.*?build_unflags =/m,"lib_deps =\nbuild_unflags =")
File.write("#{fw}/platformio.ini",ini)
def replace(path,from,to)
 s=File.read(path);raise "Unexpected source: #{path}" unless s.scan(from).size==1
 File.write(path,s.sub(from,to))
end
FileUtils.cp('experiments/uart0-race/receiver.h',"#{fw}/video/uart0_race.h")
FileUtils.cp('experiments/uart0-race/driver-hooks.h',"#{fw}/video/uart0_race_hooks.h")
replace("#{fw}/video/vdu_stream_processor.h",'void sendGeneralPoll();',"void sendGeneralPoll();\n        void uart0Race();")
replace("#{fw}/video/vdu_sys.h",'#include "ymodem.h"',"#include \"ymodem.h\"\n#include \"uart0_race.h\"")
replace("#{fw}/video/vdu_sys.h",'case VDP_GP:',"case 0xE6: { uart0Race(); } break;\n\t\tcase VDP_GP:")
replace("#{fw}/video/version.h",'"Bistromathics"','"UART0 recovery diagnostic"')
driver="#{out}/uart-idf-4.4.6.c";raise 'Wrong IDF source' unless Digest::SHA256.file(driver).hexdigest=='0a90ac006b6a0cadaac4c47ab035a54c782fb6171fda82e9dd059a3d84c4b0be'
dest="#{fw}/video/uart0_diag_driver.c";FileUtils.cp(driver,dest)
replace(dest,'static portMUX_TYPE uart_selectlock = portMUX_INITIALIZER_UNLOCKED;',"#include \"uart0_race_hooks.h\"\nstatic portMUX_TYPE uart_selectlock = portMUX_INITIALIZER_UNLOCKED;")
replace(dest,'p_uart->rx_buffer_full_flg = true;',"p_uart->rx_buffer_full_flg = true;\n                    race_after_publish(uart_num);")
replace(dest,'uart_hal_disable_intr_mask(&(uart_context[uart_num].hal), UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);',"uart_hal_disable_intr_mask(&(uart_context[uart_num].hal), UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);\n                    race_after_mask(uart_num);")
replace(dest,'uart_reenable_intr_mask(p_uart_obj[uart_num]->uart_num, UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);',"uart_reenable_intr_mask(p_uart_obj[uart_num]->uart_num, UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);\n            race_after_recovery(uart_num);")
replace(dest,'uart_intr_status = uart_hal_get_intsts_mask(&(uart_context[uart_num].hal));',"uart_intr_status = uart_hal_get_intsts_mask(&(uart_context[uart_num].hal));\n        race_note_interrupt(uart_num,uart_intr_status);")
FileUtils.cp("#{out}/ESP-IDF-LICENSE","#{fw}/ESP-IDF-LICENSE")
pins=Dir.glob("#{fw}/**/*").select{|p|File.file?(p)&&!p.include?('/.pio/')}.sort.to_h{|p|[p.delete_prefix(fw+'/'),Digest::SHA256.file(p).hexdigest]}
File.write("#{out}/source.json",JSON.pretty_generate(vdp_commit:base,vdp_gl_commit:gl,idf:'4.4.6',driver_source_sha256:Digest::SHA256.file(driver).hexdigest,files:pins)+"\n")
puts 'Prepared private VDP and instrumented IDF driver'
