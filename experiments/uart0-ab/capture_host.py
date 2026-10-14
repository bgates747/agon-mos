"""GDB-side read-only capture of an owned stalled native emulator process.

Invoked by supervise.py after no progress. Stops only that process temporarily;
does not patch registers, firmware, emulator code or UART state.
"""
import json
import hashlib
import os
from pathlib import Path
import gdb

dest = Path(os.environ['UART_AB_CAPTURE'])
inferior = gdb.selected_inferior()
assert hashlib.sha256(Path(f'/proc/{inferior.pid}/exe').read_bytes()).hexdigest() == '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
modules = [Path(obj.filename) for obj in gdb.objfiles() if Path(obj.filename).name=='flexe-vdp.so']
assert len(modules)==1
assert hashlib.sha256(modules[0].read_bytes()).hexdigest() == '77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
maps = Path(f'/proc/{inferior.pid}/maps').read_text()
(dest/'host-maps.txt').write_text(maps)
threads = []
def execute(command):
    try:
        return gdb.execute(command, to_string=True)
    except gdb.error as error:
        return f'{command}: {error}'

for thread in inferior.threads():
    thread.switch()
    threads.append(dict(number=thread.num, name=thread.name,
                        backtrace=execute('bt'),
                        registers=execute('info registers'),
                        instructions=execute('x/16i $pc')))
    if thread.name == 'ez80':
        # This layout is specific to the frozen executable, established from
        # its disassembly: start()'s CPU State is at frame RSP+118h; R14 holds
        # AgonMachine. Never apply these offsets to an unpinned runtime.
        exe = Path(f'/proc/{inferior.pid}/exe')
        if hashlib.sha256(exe.read_bytes()).hexdigest() == '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9':
            frame = gdb.newest_frame()
            while frame:
                if 'AgonMachine' in (frame.name() or '') and 'start' in frame.name():
                    state_address = int(frame.read_register('rsp')) + 0x118
                    machine_address = int(frame.read_register('r14'))
                    state = bytes(inferior.read_memory(state_address,80))
                    (dest/'cpu-state.bin').write_bytes(state)
                    (dest/'machine.bin').write_bytes(bytes(inferior.read_memory(machine_address,0x22400)))
                    (dest/'cpu-state.json').write_text(json.dumps(dict(
                        host_address=hex(state_address),machine_address=hex(machine_address),
                        guest_pc=hex(int.from_bytes(state[0x38:0x3c],'little')),
                        iff1=state[0x3e],iff2=state[0x3f],adl=state[0x41],madl=state[0x42],
                        register_data=state[8:32].hex()),indent=2)+'\n')
                    break
                frame = frame.older()
        sp = int(gdb.parse_and_eval('$sp'))
        for line in maps.splitlines():
            bounds = line.split()[0]
            start, end = [int(x,16) for x in bounds.split('-')]
            if start <= sp < end:
                start = max(start, sp-4096)
                end = min(end, sp+256*1024)
                try:
                    (dest/'ez80-stack.bin').write_bytes(bytes(inferior.read_memory(start,end-start)))
                    (dest/'ez80-stack-address.txt').write_text(hex(start)+'\n')
                except gdb.MemoryError as error:
                    (dest/'stack-error.txt').write_text(str(error)+'\n')
(dest/'host-threads.json').write_text(json.dumps(threads,indent=2)+'\n')
adapter = {}
for name, length in [('uart_pending',4),('ready',1),('failed',1),('host_to_vdp',0x100010),
                     ('session',8)]:
    try:
        address = int(gdb.parse_and_eval(f'(unsigned long)&{name}'))
        data = bytes(inferior.read_memory(address,length))
        (dest/f'adapter-{name}.bin').write_bytes(data)
        adapter[name] = dict(address=hex(address), value=data.hex() if length<16 else None)
        if name == 'session':
            pointer = int.from_bytes(data,'little')
            session_state = bytes(inferior.read_memory(pointer,0x10000))
            (dest/'adapter-session-state.bin').write_bytes(session_state)
            # Frozen adapter getters establish CPU stride70a0h, peripheral
            # pointer fa68h and UART2 pending count at 12f8h+2*11c0h.
            periph = int.from_bytes(session_state[0xfa68:0xfa70],'little')
            (dest/'adapter-peripherals.bin').write_bytes(bytes(inferior.read_memory(periph,0x5000)))
            memory = int.from_bytes(session_state[0xe140:0xe148],'little')
            dram = bytearray()
            for guest in range(0x3ffb0000,0x40000000,0x1000):
                page = int.from_bytes(bytes(inferior.read_memory(memory+0x80+(guest>>12)*8,8)),'little')
                dram.extend(bytes(inferior.read_memory(page,0x1000)) if page else bytes(0x1000))
            (dest/'vdp-dram-3ffb0000.bin').write_bytes(dram)
    except gdb.error as error:
        adapter[name] = dict(error=str(error))
(dest/'adapter.json').write_text(json.dumps(adapter,indent=2)+'\n')
# The external RAM allocation contains the native MOS application header at
# guest 040000. Match the immutable MOS header and code prefix, then retain the
# full containing allocation for offline descriptor/stack interpretation.
image = (dest/'test.bin').read_bytes()
signature = image[:64]
matches = []
for line in maps.splitlines():
    fields = line.split()
    if not fields[1].startswith('rw'):
        continue
    start, end = [int(x,16) for x in fields[0].split('-')]
    if end-start > 32*1024*1024:
        continue
    try:
        data = bytes(inferior.read_memory(start,end-start))
    except gdb.MemoryError:
        continue
    pos = data.find(signature)
    if pos >= 0:
        name = f'ram-match-{len(matches):02d}.bin'
        (dest/name).write_bytes(data)
        matches.append(dict(file=name,host_start=hex(start),guest_040000_offset=pos,
                            guest_ram_host_base=hex(start+pos-0x40000)))
(dest/'ram-matches.json').write_text(json.dumps(matches,indent=2)+'\n')
required = ['cpu-state.json','machine.bin','adapter-peripherals.bin',
            'vdp-dram-3ffb0000.bin','adapter-session-state.bin']
assert matches and all((dest/name).exists() for name in required),'Incomplete frozen-runtime capture'
(dest/'capture-complete.json').write_text(json.dumps(dict(complete=True,required_files=required))+'\n')
