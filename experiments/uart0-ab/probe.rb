#!/usr/bin/env ruby
# Add a watchdog only to a disposable diagnostic build; preserve timed image.
require 'fileutils'
d='build/uart0-ab/native-probe';FileUtils.mkdir_p(d);Dir['build/uart0-ab/native/*'].each{|p|FileUtils.cp(p,d) if File.file?(p)}
p="#{d}/app.asm";s=File.read(p)
s=s.sub("wait_drain:\n", "wait_drain:\n    call probe_watch\n")
s=s.sub("pace_work:\n","pace_work:\n    call probe_watch\n")
s=s.sub("pace_finish:\n","pace_finish:\n    call probe_watch\n")
s=s.sub("    ld (late),a","    ld (late),a\n    ld (probe_polls),a\n    ld (probe_polls+1),a\n    ld (probe_polls+2),a")
s=s.sub('    ld de,24', '    ld de,27')
s=s.sub("    ldir\n    ret\napi_open:", "    ldir\n    ld de,probe_head+1\n    ld bc,3\n    ldir\n    ret\napi_open:")
s=s.sub('saved_sp:',<<~'ASM'+"saved_sp:")
probe_head: ld hl,(0)
    ret
probe_watch:
    ld hl,(probe_polls)
    inc hl
    ld (probe_polls),hl
    ld de,200000
    or a,a
    sbc hl,de
    ret c
    ld a,i
    jp po,probe_masked
    ld a,1
    jr probe_iff_save
probe_masked:
    xor a,a
probe_iff_save:
    ld (probe_iff),a
    di
    ld a,(repeat)
    ld (probe_repeat),a
    ld a,(mode)
    ld (probe_mode),a
    ld a,(kind)
    ld (probe_kind),a
    in0 a,(0c1h)
    ld (probe_ier),a
    in0 a,(0c5h)
    ld (probe_lsr),a
    in0 a,(0c6h)
    ld (probe_msr),a
    call probe_head
    ld (probe_pointer),hl
    ld de,probe_descriptor
    ld bc,19
    ldir
    ei
    ld hl,probe_name
    ld de,probe_report
    ld bc,probe_end-probe_report
    ld a,2
    rst.lil 08h
probe_hold:
    halt
    jr probe_hold
probe_name: DB "ab-stall.dat",0
probe_polls: DB 0,0,0
probe_report: DB "ABS2"
probe_iff: DB 0
probe_repeat: DB 0
probe_mode: DB 0
probe_kind: DB 0
probe_ier: DB 0
probe_lsr: DB 0
probe_msr: DB 0
probe_pointer: DB 0,0,0
probe_descriptor: DS 19
probe_end:
ASM
File.write(p,s)
p="#{d}/native-table.inc";s=File.read(p);%w[default grouped chunk otirx].each{|m|s=s.sub(/(DW24.*#{m}_tx_rx_errors)/,"\\1,#{m}_tx_head");s=s.sub(/(XREF.*#{m}_tx_rx_errors)/,"\\1,#{m}_tx_head")};File.write(p,s)
