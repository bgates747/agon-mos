#!/usr/bin/env ruby
require 'fileutils';require 'digest';require 'json';require 'open3'
root=File.expand_path('../..',__dir__);Dir.chdir(root)
out='build/uart0-ab';FileUtils.mkdir_p(out)
# Preserve the measured private prototypes when the supported driver evolves.
# This historical comparison must not silently absorb a new session API/core.
base,status=Open3.capture2('git','show','dcc518e:src/uart0_tx.inc')
raise 'Frozen experimental baseline unavailable' unless status.success? && Digest::SHA256.hexdigest(base)=='2a086ac94ce28390ce8eff3266f193f75be4117f309690b29bac0543db0fe584'
start=base.index("    ld b,16\nservice_next:");finish=base.index("service_running:",start)
raise 'Core layout changed' unless start && finish
block=<<~'ASM'
    ld a,16
    ld (tx_block_budget),a
service_next:
    call read_msr
    bit 4,a
    jp z,service_blocked
    ld ix,(tx_head)
    ld hl,(ix+7)
    ld de,0
    ld a,(tx_block_budget)
    ld e,a
    or a,a
    sbc hl,de
    jr nc,block_budget
    add hl,de
    jr block_size
block_budget:
    ex de,hl
block_size:
    ld (tx_block_count),hl
    push hl
    pop bc
    ld hl,(ix+4)
    ld de,0c0h
    XDEF tx_write
 tx_write:
    OTIRX
    ld (ix+4),hl
    ld a,ACTIVE
    ld (ix+0),a
    ld bc,(tx_block_count)
    ld hl,(ix+10)
    add hl,bc
    ld (ix+10),hl
    ld hl,(ix+7)
    or a,a
    sbc hl,bc
    ld (ix+7),hl
    ld a,(tx_block_budget)
    sub a,c
    ld (tx_block_budget),a
    call hl_zero
    jr nz,service_more
    ld a,RELEASED
    ld (ix+0),a
    ld hl,(ix+16)
    ld (tx_head),hl
    call hl_zero
    jr nz,service_more
    ld (tx_tail),hl
    jp service_idle
service_more:
    ld a,(tx_block_budget)
    or a,a
    jp nz,service_next
ASM
scalar=<<~'ASM'.strip
block_copy:
    ld a,(hl)
    out0 (THR),a
    inc hl
    dec bc
    ld a,b
    or a,c
    jr nz,block_copy
ASM
variants={'default'=>base}
group=base[start...finish].sub("service_next:\n    call read_msr\n    bit 4,a\n    jr z,service_blocked", "    call read_msr\n    bit 4,a\n    jp z,service_blocked\nservice_next:")
variants['grouped']=base[0...start]+group+base[finish..]
%w[chunk otirx].each do |mode|
 body= mode=='chunk' ? block.sub('OTIRX',scalar) : block
 variants[mode]=base[0...start]+body+base[finish..]+"\n    XDEF tx_block_budget,tx_block_count\ntx_block_budget: DB 0\ntx_block_count: DB 0,0,0\n"
end
variants.each do |mode,src|
 src=src.gsub('jr z,service_running','jp z,service_running') unless mode=='default'
 d="#{out}/#{mode}";FileUtils.mkdir_p(d)
 File.write("#{d}/uart0_tx.inc",src)
 %w[driver.asm fixture.asm uart.linkcmd remote-build.sh].each{|f|FileUtils.cp("experiments/uart0-async/#{f}","#{d}/#{f}")}
fixture=File.read("#{d}/fixture.asm")
fixture=fixture.sub(/    END\s*\z/,"    XDEF ab_work_tick\nab_work_tick:\n    inc hl\n    jr ab_work_tick\n    END\n")
raise 'Fixture END missing' unless fixture.include?('ab_work_tick:')
File.write("#{d}/fixture.asm",fixture)
 File.write("#{d}/source.sha256",%w[driver.asm fixture.asm uart.linkcmd remote-build.sh uart0_tx.inc].map{|n|"#{Digest::SHA256.file("#{d}/#{n}").hexdigest}  #{n}\n"}.join)
end
# Reuse the pinned instruction/UART framework, not its existing benchmark main.
s=File.read('experiments/uart0-async/runner/src/main.rs').split('fn main(){').first
# Count modeled CPU execution separately from the idealized UART shifting clock.
s=s.sub('wire_done:i64,','wire_done:i64, cpu_cycles:Cell<i64>, cts_reads:usize,')
s=s.sub('wire_done:0 };','wire_done:0, cpu_cycles:Cell::new(0), cts_reads:0 };')
s=s.gsub('self.time.set(self.time.get()+1);','self.time.set(self.time.get()+1);self.cpu_cycles.set(self.cpu_cycles.get()+1);')
s=s.sub('self.time.set(self.time.get()+n as i64)','self.time.set(self.time.get()+n as i64);self.cpu_cycles.set(self.cpu_cycles.get()+n as i64)')
s=s.sub('0xc6=>{self.last_sample=', '0xc6=>{self.cts_reads+=1;self.last_sample=')
File.write("#{out}/framework.rs",s)
File.write("#{out}/source.json",JSON.pretty_generate(production_core_sha256:Digest::SHA256.hexdigest(base),variants:variants.keys.to_h{|m|[m,Digest::SHA256.file("#{out}/#{m}/uart0_tx.inc").hexdigest]},note:'Generated isolated kernels only; production source unchanged; CTS-ready performance is not physical margin qualification.')+"\n")
