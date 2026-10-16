"""Run the actual MOS FatFS/SPI path on a disposable FAT image, never a device.

The frozen frontend's directory-backed hostfs does not enforce CREATE_NEW.
Raw SD images bypass that shortcut and reproduce the hardware checkpoint bug.
"""
import argparse, hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path
from analyze import analyze

root=Path(__file__).resolve().parents[2]
b=root/'build/uart0-race/checkpoint-fix-20261014'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native',required=True,type=Path)
parser.add_argument('--label',required=True)
parser.add_argument('--engine',choices=('jit','interp'),default='jit')
parser.add_argument('--expect-hang',action='store_true')
parser.add_argument('--menu',action='store_true')
parser.add_argument('--control',choices=('badcrc','noend','nohello','sdwrite'))
a=parser.parse_args()
dest=b/a.label;dest.mkdir(parents=True,exist_ok=False)
image=dest/'card.img'
assert image.is_relative_to(b) and not image.exists()
with image.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mmd','-i',str(image),'::/uart0'],check=True)
def copyin(source,name):
    subprocess.run(['mcopy','-i',str(image),str(source),'::/'+name],check=True)
native=a.native.resolve(strict=True).read_bytes()
if a.control in ('badcrc','noend'):
    payload=bytes(((n*157+7)%254)+1 for n in range(4096))+b'\0'
    assert native.count(payload)==1
    v=bytearray(native);v[native.index(payload)+(4096 if a.control=='noend' else 0)]^=1;native=bytes(v)
elif a.control=='nohello':
    token=bytes([23,0,0xe6,2]);assert native.count(token)==1
    v=bytearray(native);v[native.index(token)+3]=3;native=bytes(v)
(dest/'race.bin').write_bytes(native);copyin(dest/'race.bin','uart0/race.bin')
if a.menu:
    assert not a.expect_hang and not a.control
    copyin(root/'build/uart0-ui/test.bin','uart0/test.bin')
    cfg=dest/'suite.cfg';cfg.write_text('board=Oryx actual MOS FatFS regression\nvdp_label=compiled recovery diagnostic\nvdp_flash=0\nphysical_receiver=0\n');copyin(cfg,'uart0/suite.cfg')
    returned=root/'build/uart0-race/hardware-return-001'
    for f in returned.iterdir():
        if f.suffix in ('.log','.dat'):copyin(f,'uart0/'+f.name)
    autoexec=b'CD /uart0\r\nLOAD test.bin\r\nRUN\r\nECHO FAT RETURN\r\n'
else:autoexec=b'CD /uart0\r\nLOAD race.bin &80000\r\nRUN &80000\r\nECHO FAT RETURN\r\n'
if a.control=='sdwrite':subprocess.run(['mmd','-i',str(image),'::/uart0/race-step.dat'],check=True)
(dest/'autoexec.txt').write_bytes(autoexec);copyin(dest/'autoexec.txt','autoexec.txt')
p=root/'.emulator/uart0-race'
pins={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in
      ('flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','esp32-firmware.bin','esp32-firmware.elf')}
art=dest/'artifacts';art.mkdir()
keys=dest/'keys';keys.write_bytes(b'')
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',
 LD_LIBRARY_PATH=str(Path.home()/'.local/lib'),AGON_FLEXE_ENGINE=a.engine,
 AGON_FLEXE_FIRMWARE=str(p/'esp32-firmware.bin'),AGON_FLEXE_ELF=str(p/'esp32-firmware.elf'),
 AGON_FLEXE_ARTIFACTS=str(art),MOS_UART_STATS=str(art/'uart.json'))
if a.menu:env.update(LD_PRELOAD=str(root/'build/uart0-ui/keys.so'),UART_SUITE_KEYS=str(keys))
command=[str(p/'runtime/flexe-agon-emulator.bin'),'--renderer','sw','--firmware','platform',
 '--mos',str(p/'mos_platform.bin'),'--vdp',str(p/'flexe-vdp.so'),
 '--sdcard-img',str(image),'-z','--precise-interrupts']
started=time.monotonic();process=None;error=None;returned=False;cursor=0
def wire():
    f=art/'mos-to-vdp.bin';return f.read_bytes() if f.exists() else b''
def wait(marker,limit=120):
    global cursor
    until=time.monotonic()+limit
    while time.monotonic()<until:
        data=wire();at=data.find(marker,cursor)
        if at>=0:cursor=at+len(marker);return
        if process.poll() is not None:raise RuntimeError('Frontend exited')
        time.sleep(.05)
    raise TimeoutError(f'{marker!r}: {wire()[-200:]!r}')
def key(value):
    with keys.open('ab') as f:f.write(value)
try:
    with (dest/'frontend.log').open('w') as log:
        process=subprocess.Popen(command,cwd=dest,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        if a.menu:
            wait(b'Press a choice key:');key(b'#9')
            wait(b'VDP flashing is unavailable in this emulator profile.');key(b'#0')
            wait(b'Press a choice key:');key(b'#8')
            wait(b'Q Back\r\nChoose:');key(b'#4')
            wait(b'Run 0010: PENDING');wait(b'Press any key for menu.');key(b'# ')
            wait(b'Press a choice key:');key(b'#q')
            wait(b'UART0 SUITE RETURN PASS')
        if a.expect_hang:
            wait(b'Case 1/2:')
            time.sleep(5)
            assert b'FAT RETURN' not in wire() and b'UART0 RACE DATA SAVED' not in wire()
        elif a.control=='sdwrite':
            wait(b'FAIL: checkpoint open/write failed')
            # A nonzero RUN result stops autoexec before ECHO, as it should.
            wait(b'/uart0 *');returned=True
        else:
            wait(b'FAT RETURN');returned=True
finally:
    if process and process.poll() is None:
        os.killpg(process.pid,signal.SIGTERM)
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
reports=dest/'reports';reports.mkdir()
subprocess.run(['mcopy','-s','-i',str(image),'::/uart0/*',str(reports)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
result=None
if a.expect_hang:
    progress=(reports/'race-step.dat').read_bytes()
    assert progress[:12]==b'URDHOST1\x01\x01\x02\x00'
    assert not any(progress[12:]) and not (reports/'race.dat').exists() and not (reports/'race-fail.dat').exists()
elif a.control=='sdwrite':
    assert b'FAIL: checkpoint open/write failed' in wire()
    assert b'Case 1/2:' not in wire() and not (reports/'race.dat').exists()
else:
    report=reports/('U0010.dat' if a.menu else 'race.dat');result=analyze(report.read_bytes())
    if a.control=='nohello':assert result['stage']==3 and not result['completed']
    elif a.control:assert result['protocol_complete'] and not all(r['integrity_passed'] for r in result['cases'])
    else:
        assert result['diagnostic_evidence_valid']
        progress=reports/('O0010.dat' if a.menu else 'race-step.dat')
        assert progress.read_bytes()==report.read_bytes()
        assert b'Setup PASS: repeated checkpoint writes' in wire()
        payload=bytes(((n*157+7)%254)+1 for n in range(4096))+b'\0'
        # No incidental RTC, logging or screen bytes may follow either ARM.
        for mode in (0,1):assert bytes([23,0,0xe6,0,mode,0])+payload in wire()
    if a.menu:
        assert 'TEST 12 PENDING' in (reports/'R0010.log').read_text()
        assert (reports/'runs.log').read_bytes().startswith((root/'build/uart0-race/hardware-return-001/runs.log').read_bytes())
        for f in (root/'build/uart0-race/hardware-return-001').iterdir():
            if f.suffix in ('.dat','.log') and f.name!='runs.log':assert (reports/f.name).read_bytes()==f.read_bytes()
stats=json.loads((art/'stats.json').read_text());uart=json.loads((art/'uart.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
assert uart['tx_drops']==uart['rx_overruns']==0
receipt=dict(passed=True,engine=a.engine,actual_MOS_FatFS=True,hostfs_disabled=True,
    old_hang_reproduced=a.expect_hang,control=a.control,returned_to_MOS=returned,integrated_menu=a.menu,
    native_sha256=hashlib.sha256(native).hexdigest(),runtime=pins,result=result,
    elapsed_seconds=round(time.monotonic()-started,3),physical_test_performed=False)
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2),flush=True)
