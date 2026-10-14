"""Headless menu/receiver/report checks; retain known-emulator failures."""
import hashlib,importlib.util,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery';profile=root/'.emulator/uart0-recovery'
engine=sys.argv[1];assert engine in ('jit','interp')
control=sys.argv[2] if len(sys.argv)>2 else None;assert control in (None,'corrupt','noreply')
app=profile/'sdcard/uart0';art=profile/'last-run';art.mkdir(exist_ok=True)
for p in Path('/proc').glob('[0-9]*'):
    try:
        if (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Recovery profile active')
    except (FileNotFoundError,PermissionError):pass
parent=build/('checks-'+engine+('-'+control if control else ''));parent.mkdir(exist_ok=True)
n=1
while (parent/f'attempt-{n:03d}').exists():n+=1
dest=parent/f'attempt-{n:03d}';dest.mkdir()
for f in art.iterdir():
    if f.is_file():f.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
original=(app/'recovery.bin').read_bytes();pins=(profile/'.runtime.sha256').read_text()
if control:
    changed=bytearray(original)
    if control=='corrupt':
        packet=(build/'bulk-packet.bin').read_bytes();assert original.count(packet)==1
        changed[original.index(packet)+14]^=1
    else:
        packet=(build/'duplex-packets.bin').read_bytes();assert original.count(packet)==1
        changed[original.index(packet)+2]=0x86 # stock keyboard-state request: no GP token
    (app/'recovery.bin').write_bytes(changed)
    (profile/'.runtime.sha256').write_text(pins.replace(hashlib.sha256(original).hexdigest()+'  sdcard/uart0/recovery.bin',hashlib.sha256(changed).hexdigest()+'  sdcard/uart0/recovery.bin'))
start=time.monotonic();returned=False;process=None
try:
    with (art/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while time.monotonic()-start<240:
            tx=art/'mos-to-vdp.bin';b=tx.read_bytes() if tx.exists() else b''
            if b'UART0 RECOVERY MENU RETURN' in b:returned=True;break
            if control and (app/'C0001.dat').exists():
                log=app/'R0001.log'
                if log.exists() and 'END run=0001 FAIL' in log.read_text():returned=True;break
            if not control:
                log=app/'R0001.log'
                if log.exists() and 'END run=0001 FAIL' in log.read_text():raise RuntimeError('Recovery/menu returned FAIL; inspect saved checkpoint')
            if process.poll() is not None:raise RuntimeError('Emulator exited early')
            time.sleep(.1)
        assert returned,'No menu return: preserve known receiver-stall possibility and checkpoints'
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
    (dest/'outcome.json').write_text(json.dumps(dict(returned=returned,elapsed_seconds=round(time.monotonic()-start,3),control=control,known_receiver_race_cleared=False))+'\n')
    (app/'recovery.bin').write_bytes(original);(profile/'.runtime.sha256').write_text(pins)
assert process.returncode==0
spec=importlib.util.spec_from_file_location('reader',root/'experiments/uart0-recovery/analyze.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
if control:
    report=(dest/'C0001.dat').read_bytes();result=reader.analyze(report);assert not result['campaign_passed']
    assert 'TEST 10 FAIL' in (dest/'R0001.log').read_text()
    assert result['state']['stage']==(3 if control=='corrupt' else 2)
    if control=='noreply':assert result['state']['failure_code']==3
else:
    report=(dest/'Y0001.dat').read_bytes();result=reader.analyze(report);assert result['campaign_passed']
    assert (dest/'Z0001.dat').read_bytes()==report and not (dest/'C0001.dat').exists()
    journal=(dest/'R0001.log').read_text();assert 'TEST 10 PASS' in journal and journal.count('RECOVERY case=')==6 and 'END run=0001 PASS' in journal
    tx=(dest/'mos-to-vdp.bin').read_bytes()
    assert tx.count((build/'bulk-packet.bin').read_bytes())==128,'Wrong sustained payload count'
    assert tx.count((build/'small-packet.bin').read_bytes())==128,'Wrong paced/duplex payload count'
    duplex=(build/'duplex-packets.bin').read_bytes();assert tx.count(duplex)==2,'Ordered duplex packet stream mismatch'
    checks=(build/'checks.bin').read_bytes()
    for i in range(0,len(checks),60):assert tx.count(checks[i:i+60])==6,'Missing full-byte receiver comparison'
    assert b'UART0 RECOVERY CAMPAIGN PASS' in tx
stats=json.loads((dest/'stats.json').read_text());uart=json.loads((dest/'uart.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')) and uart['tx_drops']==uart['rx_overruns']==0
receipt=dict(engine=engine,fixture_checks_passed=True,control=control,control_rejected=bool(control),elapsed_seconds=round(time.monotonic()-start,3),result=result,physical_qualification=False,known_receiver_race_cleared=False,human_review_passed=False,rom_sha256=hashlib.sha256((profile/'mos_platform.bin').read_bytes()).hexdigest(),native_sha256=hashlib.sha256(original).hexdigest(),menu_sha256=hashlib.sha256((app/'test.bin').read_bytes()).hexdigest(),runtime_identities=pins.splitlines())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
