"""Decode this captured diagnostic-runtime failure with exact firmware pins."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];dest=Path(sys.argv[1]).resolve()
firmware=root/'build/uart0-margin/firmware/.pio/build/esp32dev'
expected=json.loads((root/'experiments/uart0-margin/results.json').read_text())
assert hashlib.sha256((firmware/'firmware.bin').read_bytes()).hexdigest()==expected['firmware']['sha256']
# UART object fields follow the same IDF 4.4.6 DWARF layout as the earlier
# frozen-runtime investigation; the global array address comes from this ELF.
nm=Path.home()/'.platformio/packages/toolchain-xtensa-esp32/bin/xtensa-esp32-elf-nm'
lines=subprocess.check_output([str(nm),'-n',str(firmware/'firmware.elf')],text=True).splitlines()
array=int(next(l.split()[0] for l in lines if l.endswith(' p_uart_obj')),16)
dram=(dest/'vdp-dram-3ffb0000.bin').read_bytes()
def dnum(address,n=4):
    offset=address-0x3ffb0000;assert 0<=offset and offset+n<=len(dram)
    return int.from_bytes(dram[offset:offset+n],'little')
obj=dnum(array+8);ring=dnum(obj+232)
periph=(dest/'adapter-peripherals.bin').read_bytes();uart=0x270+2*0x11c0
pnum=lambda offset,n=4:int.from_bytes(periph[uart+offset:uart+offset+n],'little')
machine=(dest/'machine.bin').read_bytes();mnum=lambda offset,n=1:int.from_bytes(machine[offset:offset+n],'little')
symbols={l.split()[2]:int(l.split()[0],16) for l in (root/'build/uart0-mos/symbols.txt').read_text().splitlines()}
driver=None
for match in json.loads((dest/'ram-matches.json').read_text()):
    data=(dest/match['file']).read_bytes();base=match['guest_040000_offset']-0x40000
    def read(address,n=1):
        offset=base+address;assert 0<=offset and offset+n<=len(data)
        return int.from_bytes(data[offset:offset+n],'little')
    try:
        head=read(symbols['tx_head'],3)
        driver=dict(opened=read(symbols['tx_opened']),batch=read(symbols['tx_cts_batch']),head=hex(head),
                    remaining=read(head+7,3),accepted=read(head+10,3))
        break
    except AssertionError:pass
assert driver is not None
result=dict(scope='Snapshot of recurrence consistent with previously traced VDP recovery race; not a new traced write history or fix',
    firmware_sha256=hashlib.sha256((firmware/'firmware.bin').read_bytes()).hexdigest(),
    firmware_elf_sha256=hashlib.sha256((firmware/'firmware.elf').read_bytes()).hexdigest(),
    frontend_sha256='412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9',
    adapter_sha256='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd',
    cpu=json.loads((dest/'cpu-state.json').read_text()),driver=driver,
    ez80_uart=dict(ier=mnum(0x1a2),cts=mnum(0x19e),delta=mnum(0x1a0),fifo=mnum(0x128,8),shift=mnum(0x188,4)),
    vdp_uart=dict(fifo=pnum(0x1088,2),raw=hex(pnum(0x11b0)),enable=hex(pnum(0x11b4))),
    receiver=dict(object=hex(obj),full=dnum(obj+28,1),buffered=dnum(obj+20),
                  requested_mask=hex(dnum(obj+176)),ring=hex(ring),waiting=dnum(ring+56)),
    physical_qualification=False,known_receiver_race_cleared=False)
assert result['vdp_uart']['fifo']==128 and pnum(0x11b4)&0x101==0
assert result['receiver']['full']==result['receiver']['buffered']==result['receiver']['waiting']==0
(dest/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
