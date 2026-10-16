"""Retain every run; emulator checks do not establish physical driver behavior."""
import hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
from analyze import analyze
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race';p=root/'.emulator/uart0-race'
engine=sys.argv[1];assert engine in ('jit','interp');app=p/'sdcard/uart0';art=p/'last-run';art.mkdir(exist_ok=True)
menu='--menu' in sys.argv
control=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='--menu' else None;assert control in (None,'badcrc','noend','nohello')
assert not(menu and control)
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
original=(app/'race.bin').read_bytes();pins=(p/'.runtime.sha256').read_text()
if control:
    changed=bytearray(original)
    if control=='nohello':
        token=bytes([23,0,0xe6,2]);assert original.count(token)==1
        changed[original.index(token)+3]=3
    else:
        payload=bytes(((i*157+7)%254)+1 for i in range(4096))+b'\0';assert original.count(payload)==1
        changed[original.index(payload)+(4096 if control=='noend' else 0)]^=1
    (app/'race.bin').write_bytes(changed)
    (p/'.runtime.sha256').write_text(pins.replace(hashlib.sha256(original).hexdigest()+'  sdcard/uart0/race.bin',hashlib.sha256(changed).hexdigest()+'  sdcard/uart0/race.bin'))
evidence=b/('checks-'+engine+('-menu' if menu else '-'+control if control else ''));evidence.mkdir(exist_ok=True);n=1
while (evidence/f'attempt-{n:03d}').exists():n+=1
dest=evidence/f'attempt-{n:03d}';dest.mkdir()
for f in app.glob('*.dat'):shutil.copyfile(f,dest/('prior-'+f.name));f.unlink()
for f in art.iterdir():
    if f.is_file():f.unlink()
process=None;start=time.monotonic();error=None
try:
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
    with (art/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while time.monotonic()-start<240:
            f=art/'mos-to-vdp.bin';text=f.read_bytes() if f.exists() else b''
            if b'UART0 RACE RETURN' in text:break
            if process.poll() is not None:raise RuntimeError('Emulator exited')
            time.sleep(.1)
        else:raise RuntimeError('No return within 240 seconds')
        report=app/('U0001.dat' if menu else 'race.dat');assert report.exists(),'No completed report'
        result=analyze(report.read_bytes())
        if control=='nohello':assert result['stage']==3 and not result['completed']
        elif control:
            assert result['protocol_complete'] and not result['diagnostic_evidence_valid']
            assert any(not r['integrity_passed'] for r in result['cases'])
        else:
            assert result['protocol_complete']
            assert all(r['integrity_passed'] for r in result['cases']),'Payload/driver errors'
        if menu:
            assert (app/'O0001.dat').read_bytes()==report.read_bytes()
            journal=(app/'R0001.log').read_text()
            assert 'TEST 12 PENDING' in journal and 'END run=0001 PENDING' in journal
            assert 'physical_target=0 evidence_valid=1' in journal
            assert journal in (app/'runs.log').read_text()
except Exception as e:error=repr(e)
finally:
    if process and process.poll() is None:
        for q in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(q.name))==process.pid and (q/'exe').resolve()==(p/'runtime/flexe-agon-emulator.bin').resolve():os.kill(int(q.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    for f in [*art.iterdir(),*app.glob('*.dat')]:
        if f.is_file():shutil.copyfile(f,dest/f.name)
    (dest/'runtime.sha256').write_text((p/'.runtime.sha256').read_text())
    (app/'race.bin').write_bytes(original);(p/'.runtime.sha256').write_text(pins)
try:
    stats=json.loads((dest/'stats.json').read_text());uart=json.loads((dest/'uart.json').read_text())
    assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')),stats
    assert uart['tx_drops']==uart['rx_overruns']==0,uart
except Exception as e:
    if error is None:error=repr(e)
receipt=dict(engine=engine,integrated_menu=menu,control=control,control_rejected=bool(control) and error is None,elapsed_seconds=round(time.monotonic()-start,3),error=error,protocol_integrity_passed=error is None and not control,physical_test_performed=False,release_qualified=False,runtime_identities=pins.splitlines())
resultfile=dest/('U0001.dat' if menu else 'race.dat')
if resultfile.exists():receipt['result']=analyze(resultfile.read_bytes())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if error:raise RuntimeError(error)
(evidence/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
