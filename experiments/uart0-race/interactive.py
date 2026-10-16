"""Headless real SDL input: submenu, report collision, safe flash refusal, return."""
import hashlib,json,os,shutil,signal,subprocess,time
from pathlib import Path
from analyze import analyze
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race';p=root/'.emulator/uart0-race';app=p/'sdcard/uart0';art=p/'last-run';art.mkdir(exist_ok=True)
parent=b/'checks-interactive';parent.mkdir(exist_ok=True);n=1
while (parent/f'attempt-{n:03d}').exists():n+=1
dest=parent/f'attempt-{n:03d}';dest.mkdir()
assert not list(app.glob('*.dat')) and not (app/'runs.log').exists()
(app/'U0001.dat').write_bytes(b'PRESERVE PRIOR DIAGNOSTIC RESULT\n')
keys=b/'keys-input';keys.write_bytes(b'')
for f in art.iterdir():
    if f.is_file():f.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
process=None;cursor=0;started=time.monotonic()
def wire():
    f=art/'mos-to-vdp.bin';return f.read_bytes() if f.exists() else b''
def wait(marker,limit=180):
    global cursor
    end=time.monotonic()+limit
    while time.monotonic()<end:
        data=wire();at=data.find(marker,cursor)
        if at>=0:cursor=at+len(marker);return
        if process.poll() is not None:raise RuntimeError('Interactive emulator exited')
        if b'Run 0002: FAIL' in data:raise RuntimeError('Diagnostic menu failure')
        time.sleep(.1)
    raise TimeoutError(f'{marker!r}: {wire()[-160:]!r}')
def key(value):
    with keys.open('ab') as f:f.write(value)
try:
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE='jit',LD_PRELOAD=str(root/'build/uart0-suite/keys.so'),UART_SUITE_KEYS=str(keys))
    with (art/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        wait(b'Press a choice key:');key(b'8');wait(b'Q Back\r\nChoose:');key(b'4')
        wait(b'Run 0002: PENDING');wait(b'Press any key for menu.');key(b' ')
        wait(b'Press a choice key:');key(b'9');wait(b'VDP flashing is unavailable in this emulator profile.');key(b'2')
        wait(b'VDP flashing unavailable in this emulator profile; updater not launched.')
        wait(b'Run 0003: SKIP');wait(b'Press a choice key:');key(b'q')
        wait(b'UART0 SUITE RETURN PASS');wait(b'UART0 RACE RETURN')
finally:
    if process and process.poll() is None:
        for q in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(q.name))==process.pid and (q/'exe').resolve()==(p/'runtime/flexe-agon-emulator.bin').resolve():os.kill(int(q.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    for f in [*art.iterdir(),*app.glob('*.dat'),*app.glob('*.log')]:
        if f.is_file():shutil.copyfile(f,dest/f.name)
assert (app/'U0001.dat').read_bytes()==b'PRESERVE PRIOR DIAGNOSTIC RESULT\n'
assert not (app/'R0001.log').exists()
data=(app/'U0002.dat').read_bytes();result=analyze(data);assert result['diagnostic_evidence_valid']
assert data==(app/'O0002.dat').read_bytes() and not (app/'V0002.dat').exists()
detail=(app/'R0002.log').read_text();assert 'TEST 12 PENDING' in detail and 'evidence_valid=1' in detail
flash=(app/'R0003.log').read_text();assert 'FLASH_SKIP' in flash and 'END run=0003 SKIP' in flash and 'FLASH_HANDOFF' not in flash
index=(app/'runs.log').read_text();assert detail in index and flash in index
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
receipt=dict(interactive_checks_passed=True,orphan_preserved=True,emulator_flash_blocked=True,returned_to_MOS=True,
 elapsed_seconds=round(time.monotonic()-started,3),physical_test_performed=False,human_review_passed=False,
 native_sha256=hashlib.sha256((app/'race.bin').read_bytes()).hexdigest(),menu_sha256=hashlib.sha256((app/'test.bin').read_bytes()).hexdigest(),VDP_sha256=hashlib.sha256((p/'esp32-firmware.bin').read_bytes()).hexdigest(),result=result)
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
