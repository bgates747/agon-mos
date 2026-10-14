"""GDB hardware watchpoints for the frozen VDP RX recovery ordering.

Stops on a disable with a cleared recovery flag. The supervisor then captures
and resumes the emulator; this is diagnostic evidence, never qualification.
"""
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import time
import gdb

dest = Path(os.environ['UART_AB_CAPTURE'])
inferior = gdb.selected_inferior()
module = next(Path(o.filename) for o in gdb.objfiles() if Path(o.filename).name=='flexe-vdp.so')
assert hashlib.sha256(module.read_bytes()).hexdigest()=='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
def num(address,length=4):
    return int.from_bytes(bytes(inferior.read_memory(address,length)),'little')
session = num(int(gdb.parse_and_eval('(unsigned long)&session')),8)
memory = num(session+0xe140,8)
periph = num(session+0xfa68,8)
def guest(address,length=4):
    page = num(memory+0x80+(address>>12)*8,8)
    assert page
    return num(page+(address&0xfff),length)
obj = guest(0x3ffc6238)
assert 0x3ffb0000<=obj<0x40000000
flag_page = num(memory+0x80+((obj+28)>>12)*8,8)
flag_address = flag_page+((obj+28)&0xfff)
ena_address = periph+0x270+2*0x11c0+0x11b4
records = deque(maxlen=4096)
sequence = 0
class Watch(gdb.Breakpoint):
    def __init__(self,label,address,size):
        self.label = label
        self.previous = num(address,size)
        self.address = address
        self.size = size
        super().__init__(f'*({"unsigned int" if size==4 else "unsigned char"}*){address}',
                         type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_WRITE,internal=True)
    def stop(self):
        global sequence
        sequence += 1
        value = num(self.address,self.size)
        ena = num(ena_address)
        flag = num(flag_address,1)
        ring = guest(obj+232)
        row = dict(sequence=sequence,event=self.label,previous=self.previous,value=value,
                   int_ena=hex(ena),full=flag,buffered=guest(obj+20),ring_waiting=guest(ring+56),
                   core_pc=[hex(num(session+core*0x70a0+0x100)) for core in (0,1)],
                   ticks=guest(0x3ffc66c8),host_monotonic=time.monotonic())
        self.previous = value
        records.append(row)
        anomaly = self.label=='int_ena' and ena&0x101==0 and flag==0
        if anomaly or sequence<=8 or sequence%64==0:
            (dest/'rx-write-history.json').write_text(json.dumps(dict(
                anomaly=anomaly,total_events=sequence,records=list(records)),indent=2)+'\n')
        return anomaly
watchers = [Watch('full_flag',flag_address,1),Watch('int_ena',ena_address,4)]
(dest/'rx-watch-ready.json').write_text(json.dumps(dict(object=hex(obj),flag_host=hex(flag_address),
    ena_host=hex(ena_address),initial_ena=hex(num(ena_address))))+'\n')
def on_stop(event):
    previous = dest/'rx-write-history.json'
    if previous.exists() and json.loads(previous.read_text())['anomaly']:
        return
    previous.write_text(json.dumps(dict(anomaly=False,total_events=sequence,records=list(records)),indent=2)+'\n')
gdb.events.stop.connect(on_stop)
