#!/usr/bin/env ruby
require 'fileutils';require 'digest';require 'json'
root=File.expand_path('../..',__dir__);Dir.chdir(root)
out='build/uart0-batching';FileUtils.mkdir_p(out)
FileUtils.mkdir_p("#{out}/source")
%w[uart0_tx.inc uart0_async.asm].each{|name|FileUtils.cp("src/#{name}","#{out}/source/#{name}")}
%w[otirx scalar].each do |mode|
 d="#{out}/#{mode}";FileUtils.mkdir_p(d)
 FileUtils.cp('src/uart0_tx.inc',d)
 %w[driver.asm fixture.asm uart.linkcmd remote-build.sh].each{|f|FileUtils.cp("experiments/uart0-async/#{f}",d)}
 if mode=='scalar'
  p="#{d}/driver.asm";File.write(p,File.read(p).sub('UART0_BATCH_SCALAR EQU 0','UART0_BATCH_SCALAR EQU 1'))
 end
 File.write("#{d}/source.sha256",%w[driver.asm fixture.asm uart.linkcmd remote-build.sh uart0_tx.inc].map{|n|"#{Digest::SHA256.file("#{d}/#{n}").hexdigest}  #{n}\n"}.join)
end
# Compile the real driver; extend the independent instruction/UART harness with
# a CTS allowance oracle and source-boundary tests, not a translated driver.
s=File.read('experiments/uart0-async/runner/src/main.rs').split('fn main(){').first
s=s.sub('wire_done:i64,','wire_done:i64, batch_addr:usize, allowance:usize, group_writes:usize,')
s=s.sub('wire_done:0 };','wire_done:0, batch_addr:0, allowance:0, group_writes:0 };')
s=s.sub('0xc6=>{self.last_sample=self.cts;', '0xc6=>{self.allowance=if self.cts{self.mem[self.batch_addr].max(1)as usize}else{0};self.group_writes=0;self.last_sample=self.cts;')
s=s.sub('assert!(self.last_sample,"CTS guard missing");','assert!(self.last_sample,"CTS guard missing");assert!(self.allowance>0,"CTS group allowance exceeded");self.allowance-=1;self.group_writes+=1;')
s=s.sub('let mut u=Uart::new(image);','let mut u=Uart::new(image);u.batch_addr=s["tx_cts_batch"];')
s=s.sub('fn open(&mut self){assert_eq!(self.call("tx_open",0,0,0).0,0)}','fn open(&mut self){assert_eq!(self.call("tx_open",0,0,0).0,0);let n=env::var("UART_BATCH_SIZE").unwrap().parse::<u32>().unwrap();assert_eq!(self.call("tx_set_cts_batch",0,0,n<<8).0,0)}')
# Existing stall oracle is exact per-byte. For batches allow the bounded tail;
# keep all its IO-edge wakeup sweeps, storm detection and final byte comparison.
s=s.sub('assert_eq!(r.u.writes.len(),cut);assert_eq!(r.state(t).1,cut as u32);','let count=r.u.writes.len();let n=r.byte("tx_cts_batch")as usize;assert!(count>=cut && count<=cut+n-1);assert_eq!(r.state(t).1,count as u32);')
FileUtils.mkdir_p("#{out}/runner/src")
File.write("#{out}/runner/src/main.rs",s+File.read('experiments/uart0-batching/checks.rs'))
FileUtils.cp('experiments/uart0-async/runner/Cargo.lock',"#{out}/runner/")
File.write("#{out}/runner/Cargo.toml",<<~TOML)
[package]
name="mos-uart0-async-qualification"
version="0.1.0"
edition="2021"
publish=false
[dependencies]
ez80={path="../../uart0-async/ez80-model"}
TOML
File.write("#{out}/source.json",JSON.pretty_generate(core_sha256:Digest::SHA256.file('src/uart0_tx.inc').hexdigest,wrapper_sha256:Digest::SHA256.file('src/uart0_async.asm').hexdigest,scope:'Experimental ABI1.2; public session API with OTIRX and isolated scalar comparison; no production approval.')+"\n")
