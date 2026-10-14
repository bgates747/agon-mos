"""Exercise numbered submenu, short/extended paths and orphan preservation."""
import hashlib,importlib.util,json,os,shutil,signal,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery';profile=root/'.emulator/uart0-recovery'
app=profile/'sdcard/uart0';art=profile/'last-run';art.mkdir(exist_ok=True)
parent=build/'checks-interactive';parent.mkdir(exist_ok=True);n=1
while (parent/f'attempt-{n:03d}').exists():n+=1
dest=parent/f'attempt-{n:03d}';dest.mkdir()
for f in art.iterdir():
    if f.is_file():f.unlink()
assert not list(app.glob('*.dat')) and not (app/'runs.log').exists()
(app/'Y0001.dat').write_text('ORPHAN RECOVERY RESULT - PRESERVE\n')
keys=build/'keys-input';keys.write_bytes(b'')
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
process=None;cursor=0;start=time.monotonic()
def wire():
    p=art/'mos-to-vdp.bin';return p.read_bytes() if p.exists() else b''
def wait(marker,limit=120):
    global cursor
    end=time.monotonic()+limit
    while time.monotonic()<end:
        b=wire();at=b.find(marker,cursor)
        if at>=0:cursor=at+len(marker);return
        if process.poll() is not None:raise RuntimeError('Interactive emulator exited early')
        if b'Run 0002: FAIL' in b or b'Run 0003: FAIL' in b:raise RuntimeError('Interactive campaign FAIL')
        time.sleep(.1)
    raise TimeoutError(f'Waiting for {marker!r}; tail={wire()[-200:]!r}')
def key(value):
    with keys.open('ab') as f:f.write(value)
try:
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE='jit',LD_PRELOAD=str(root/'build/uart0-suite/keys.so'),UART_SUITE_KEYS=str(keys))
    with (art/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=profile,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        wait(b'Press a choice key:');key(b'8');wait(b'Q Back\r\nChoose:');key(b'q')
        wait(b'Press a choice key:');key(b'8');wait(b'Q Back\r\nChoose:');key(b'2')
        wait(b'Run 0002: PASS',180);wait(b'Press any key for menu.');key(b' ')
        wait(b'Press a choice key:');key(b'8');wait(b'Q Back\r\nChoose:');key(b'3')
        wait(b'Run 0003: PASS',480);wait(b'Press any key for menu.');key(b' ')
        wait(b'Press a choice key:');key(b'q');wait(b'UART0 SUITE RETURN PASS');wait(b'UART0 RECOVERY MENU RETURN')
finally:
    if process and process.poll() is None:
        for p in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(p.name))==process.pid and (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():os.kill(int(p.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    for f in [*art.iterdir(),*app.glob('*.dat'),*app.glob('*.log')]:
        if f.is_file():shutil.copyfile(f,dest/f.name)
assert process.returncode==0
assert (app/'Y0001.dat').read_text()=='ORPHAN RECOVERY RESULT - PRESERVE\n'
spec=importlib.util.spec_from_file_location('reader',root/'experiments/uart0-recovery/analyze.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
results={}
for run,count,test in ((2,6,10),(3,24,11)):
    data=(app/f'Y{run:04d}.dat').read_bytes();result=reader.analyze(data)
    assert result['campaign_passed'] and len(result['records'])==count
    assert (app/f'Z{run:04d}.dat').read_bytes()==data and not (app/f'C{run:04d}.dat').exists()
    journal=(app/f'R{run:04d}.log').read_text();assert f'TEST {test} PASS' in journal and f'END run={run:04d} PASS' in journal
    results[str(run)]=result
assert not (app/'R0001.log').exists() and (app/'runs.log').read_text().count('END run=')==2
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
receipt=dict(interactive_checks_passed=True,short_and_extended_passed=True,real_SDL_key_events=True,orphan_preserved=True,
 runs=[2,3],elapsed_seconds=round(time.monotonic()-start,3),results=results,human_review_passed=False,physical_qualification=False,known_receiver_race_cleared=False,
 native_sha256=hashlib.sha256((app/'recovery.bin').read_bytes()).hexdigest(),menu_sha256=hashlib.sha256((app/'test.bin').read_bytes()).hexdigest(),runtime_identities=(profile/'.runtime.sha256').read_text().splitlines())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
