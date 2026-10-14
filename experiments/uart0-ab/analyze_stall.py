"""Decode frozen-runtime snapshots; fail closed on other binary layouts."""
import hashlib
import json
from pathlib import Path
import re
import sys

dest = Path(sys.argv[1])
pins = (dest/'runtime.sha256').read_text() if (dest/'runtime.sha256').exists() else (dest.parent/'runtime.sha256').read_text()
assert '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9' in pins
assert '77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd' in pins
assert '51f196eb7b84ed79394a9fde1dff832ad479417c360525c69582fd093c3a0a3a' in pins
parent = dest if (dest/'app.map').exists() else dest.parent
symbols = {m[0]:int(m[1],16) for m in re.findall(r'^(\w+)\s+C:([0-9A-Fa-f]{6})\s', (parent/'app.map').read_text(), re.M)}
private = {m[1]:0x40000+int(m[0],16) for m in re.findall(r'^([0-9A-Fa-f]{6})\s+[^\n]*?\b([a-z_][a-z_0-9]*):', (parent/'app.lst').read_text(),re.M)}
matches = json.loads((dest/'ram-matches.json').read_text())
matches = [m for m in matches if m['guest_040000_offset']<4096 and (dest/m['file']).stat().st_size>=0x80000]
assert len(matches)==1,matches
match = matches[0]
ram = (dest/match['file']).read_bytes()
offset = match['guest_040000_offset']
assert ram[offset:offset+64]==(parent/'test.bin').read_bytes()[:64]
def read(address,length):
    index = address-0x40000+offset
    assert index>=0 and index+length<=len(ram),(hex(address),length)
    return ram[index:index+length]
def number(address,length=3):
    return int.from_bytes(read(address,length),'little')

mode = number(private['mode'],1)
result = dict(native_sha256=hashlib.sha256((parent/'test.bin').read_bytes()).hexdigest(),
              repeat=number(private['repeat'],1)+1,mode=mode,phase=number(private['kind'],1),
              work=number(private['work']),irqs=number(private['irqs']),
              mos_clock=number(number(private['sysvars'])),
              cpu=json.loads((dest/'cpu-state.json').read_text()) if (dest/'cpu-state.json').exists() else None)
driver = ['default','default','grouped','chunk','otirx'][mode]
head = number(symbols[f'{driver}_tx_head'])
result['driver'] = dict(name=driver,head=hex(head),ier=number(symbols[f'{driver}_tx_ier'],1))
if head:
    result['driver']['descriptor'] = dict(state=number(head,1),ticket=number(head+1),
                                         source=hex(number(head+4)),remaining=number(head+7),
                                         accepted=number(head+10),length=number(head+13))
if (dest/'machine.bin').exists():
    machine = (dest/'machine.bin').read_bytes()
    get = lambda i,n=1:int.from_bytes(machine[i:i+n],'little')
    result['ez80_uart'] = dict(ier=get(0x1a2),cts=get(0x19e),delta=get(0x1a0),
                              rx_errors=get(0x1a1),rx_fifo=get(0x108,8),
                              tx_fifo=get(0x128,8),shift_present=get(0x188,4))
if (dest/'adapter-peripherals.bin').exists():
    periph = (dest/'adapter-peripherals.bin').read_bytes()
    num = lambda i,n=4:int.from_bytes(periph[i:i+n],'little')
    uart = 0x270+2*0x11c0
    result['vdp_uart2'] = dict(fifo_count=num(uart+0x1088,2),int_raw=hex(num(uart+0x11b0)),
                               int_ena=hex(num(uart+0x11b4)))
    queue = (dest/'adapter-host_to_vdp.bin').read_bytes()
    result['adapter'] = dict(ingress_queue=int.from_bytes(queue[0x100008:0x100010],'little'),
                             uart_pending=int.from_bytes((dest/'adapter-uart_pending.bin').read_bytes(),'little'))
if (dest/'vdp-dram-3ffb0000.bin').exists():
    dram = (dest/'vdp-dram-3ffb0000.bin').read_bytes()
    def dnum(address,length=4):
        index = address-0x3ffb0000
        assert 0<=index and index+length<=len(dram),hex(address)
        return int.from_bytes(dram[index:index+length],'little')
    # Addresses and offsets come from this exact firmware ELF's DWARF.
    obj = dnum(0x3ffc6230+8)
    ring = dnum(obj+232)
    result['vdp_driver'] = dict(object=hex(obj),buffered=dnum(obj+20),
                               buffer_size=dnum(obj+24),full=dnum(obj+28,1),
                               current_read=dnum(obj+32),stash=dnum(obj+172,1),
                               requested_rx_mask=hex(dnum(obj+176)),
                               ring=hex(ring),ring_size=dnum(ring),ring_waiting=dnum(ring+56),
                               freertos_ticks=dnum(0x3ffc66c8))
    session = (dest/'adapter-session-state.bin').read_bytes()
    result['vdp_cpu_pc'] = [hex(int.from_bytes(session[i+0x100:i+0x104],'little')) for i in (0,0x70a0)]
    result['receive_wakeup_failure'] = (result['vdp_uart2']['fifo_count']>0 and
        int(result['vdp_uart2']['int_ena'],16)&0x101==0 and
        result['vdp_driver']['ring_waiting']==0 and result['vdp_driver']['full']==0)
(dest/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
