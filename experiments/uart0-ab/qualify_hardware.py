"""Check relocated child, menu reporting and repeat numbering off-device.

Passing this integration check does not clear the known receiver race or
qualify hardware. The Author explicitly selected physical comparison testing.
"""
import hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'.emulator/uart0-ab-hardware-auto';app=p/'sdcard/uart0';art=p/'last-run'
engine=sys.argv[1];assert engine in ('jit','interp')
repeats=int(sys.argv[2]) if len(sys.argv)>2 else 1
base=root/f'build/uart0-ab/hardware-check-{engine}';base.mkdir(exist_ok=True)
if (base/'receipt.json').exists():(base/'receipt.json').unlink()
number=1
while (base/f'attempt-{number:03d}').exists():number+=1
dest=base/f'attempt-{number:03d}';dest.mkdir()
art.mkdir(exist_ok=True)
for f in art.iterdir():
    if f.is_file():f.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
start=time.monotonic();returned=False
with (art/'frontend.log').open('w') as log:
    proc=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:
        while time.monotonic()-start<240:
            tx=art/'mos-to-vdp.bin';data=tx.read_bytes() if tx.exists() else b''
            assert b'Error executing autoexec.txt' not in data,'Autoexec command failed'
            if b'UART0 AB MENU RETURN' in data:returned=True;break
            assert proc.poll() is None,'Emulator exited early'
            time.sleep(.1)
        assert returned,'Menu integration timeout (known receiver race remains possible)'
    finally:
        if proc.poll() is None:
            for d in Path('/proc').glob('[0-9]*'):
                try:
                    if os.getpgid(int(d.name))==proc.pid and (d/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():os.kill(int(d.name),signal.SIGTERM)
                except (FileNotFoundError,PermissionError,ProcessLookupError):pass
            proc.wait(timeout=10)
        for f in [*art.iterdir(),*app.glob('*.dat'),*app.glob('R????.log'),app/'runs.log']:
            if f.is_file():shutil.copyfile(f,dest/f.name)
        (dest/'outcome.json').write_text(json.dumps(dict(returned=returned,elapsed_seconds=time.monotonic()-start))+'\n')
assert proc.returncode==0
for run in range(1,repeats+1):
    b=(app/f'A{run:04d}.dat').read_bytes()
    assert len(b)==488 and b[:8]==b'UAB1\x01\x1e\x10\0'
    for n in range(30):
        r=b[8+n*16:24+n*16];mode=n%10//2
        if n//10&1:mode=4-mode
        assert r[0]==n//10 and r[1]==mode and r[2]==n%2
        assert int.from_bytes(r[3:6],'little')>0 and r[13:]==bytes(3)
    journal=(app/f'R{run:04d}.log').read_text()
    assert f'END run={run:04d} PASS' in journal and 'TEST 8 PASS' in journal and journal.count('AB repeat=')==30
    assert not (app/f'X{run:04d}.dat').exists()
tx=(art/'mos-to-vdp.bin').read_bytes()
native=root/'build/uart0-ab/hardware-native'
assert tx.count((native/'bulk-packet.bin').read_bytes())==45*repeats
assert tx.count((native/'pace-packet.bin').read_bytes())==900*repeats
uart=json.loads((art/'uart.json').read_text());stats=json.loads((art/'stats.json').read_text())
assert uart['tx_drops']==uart['rx_overruns']==0 and not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
receipt=dict(menu_integration_passed=True,engine=engine,repeats=repeats,phases=30*repeats,
    elapsed_seconds=round(time.monotonic()-start,3),native_sha256=hashlib.sha256((app/'ab.bin').read_bytes()).hexdigest(),
    menu_sha256=hashlib.sha256((app/'test.bin').read_bytes()).hexdigest(),
    physical_qualification=False,known_receiver_race_cleared=False,
    runtime_identities=(p/'.runtime.sha256').read_text().splitlines())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(base/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
