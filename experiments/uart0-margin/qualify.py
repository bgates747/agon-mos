"""Protocol qualification only: emulator FIFO/RTS semantics are unqualified."""
import hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-margin'
engine=sys.argv[1];assert engine in ('jit','interp')
menu='--menu' in sys.argv
profile=root/('.emulator/uart0-margin-menu-auto' if menu else '.emulator/uart0-margin')
control=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='--menu' else None
assert control in (None,'badcrc','noend')
assert not(menu and control)
app=profile/'sdcard/uart0';artifacts=profile/'last-run';artifacts.mkdir(exist_ok=True)
for p in app.glob('*.dat'):p.unlink()
if menu:
    for p in app.glob('*.log'):p.unlink()
for p in artifacts.iterdir():
    if p.is_file():p.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
original=(app/'margin.bin').read_bytes();original_pins=(profile/'.runtime.sha256').read_text()
if control:
    payload=bytes(((n*157+7)%254)+1 for n in range(4096))+b'\0'
    assert original.count(payload)==1 and original.count(b'\xfe\x2a')==1
    bad=bytearray(original);at=original.index(payload)
    bad[at if control=='badcrc' else at+4096]^=1
    bad[original.index(b'\xfe\x2a')+1]=1
    (app/'margin.bin').write_bytes(bad)
    old=hashlib.sha256(original).hexdigest();new=hashlib.sha256(bad).hexdigest()
    (profile/'.runtime.sha256').write_text(original_pins.replace(old+'  sdcard/uart0/margin.bin',new+'  sdcard/uart0/margin.bin'))
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
process=None;started=time.monotonic();returned=False
try:
    with (artifacts/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=profile,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while time.monotonic()-started<300:
            p=artifacts/'mos-to-vdp.bin';b=p.read_bytes() if p.exists() else b''
            if b'UART0 MARGIN TRANSPORT FAIL' in b:raise RuntimeError('Diagnostic transport failed')
            if (b'UART0 MARGIN MENU RETURN' if menu else b'UART0 MARGIN RETURN') in b:returned=True;break
            if process.poll() is not None:raise RuntimeError('Emulator exited early')
            time.sleep(.1)
        assert returned,'Timeout before MOS return'
finally:
    if process and process.poll() is None:
        for p in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(p.name))==process.pid and (p/'exe').resolve()==(profile/'flexe-agon-emulator.bin').resolve():os.kill(int(p.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    dest=build/('evidence-'+engine+('-menu' if menu else '-'+control if control else ''));dest.mkdir(exist_ok=True)
    for p in [*artifacts.iterdir(),*app.glob('*.dat'),*app.glob('*.log')]:
        if p.is_file():shutil.copyfile(p,dest/p.name)
    (app/'margin.bin').write_bytes(original)
    (profile/'.runtime.sha256').write_text(original_pins)
assert process.returncode==0
report=app/('H0002.dat' if menu else 'margin.dat')
assert report.exists(),'No measurement report'
b=report.read_bytes();assert len(b)==2028 and b[:12]==b'URMHOST1\x01\x00\x2a\x00',b[:12]
if menu:
    first=(app/'R0001.log').read_text();second=(app/'R0002.log').read_text()
    for n in (1,2,3,6):assert f'TEST {n} PASS' in first,first
    assert 'TEST 7 PENDING' in second and 'MARGIN physical_target=0' in second,second
expected=json.loads((build/'expected.json').read_text())
rows=[b[12+n*48:60+n*48] for n in range(42)]
u32=lambda row,at:int.from_bytes(row[at:at+4],'little')
if control:
    row=rows[0];assert row[:4]==b'URM1' and row[45]==1 and row[47]==0
    if control=='badcrc':assert u32(row,36)==4096 and u32(row,40)!=expected['payload_crc32'] and row[44]==0
    else:assert row[44]&4 and u32(row,36)==4097
else:
    for row,(threshold,hold) in zip(rows,expected['cases']):
        assert row[:7]==b'URM1'+bytes([1,threshold,hold])
        assert u32(row,36)==4096 and u32(row,40)==expected['payload_crc32'],row.hex()
        assert row[44]==0 and row[45]==1 and row[47]==0,row.hex()
stats=json.loads((artifacts/'stats.json').read_text());uart=json.loads((artifacts/'uart.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')),stats
assert uart['tx_drops']==uart['rx_overruns']==0,uart
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
receipt=dict(engine=engine,elapsed_seconds=round(time.monotonic()-started,3),returned_to_mos=True,
control=control,verified_payloads=1 if control else 42,control_rejected=bool(control),
physical_margin_qualified=False,emulator_metrics_unqualified=True,backend=stats,uart=uart,
integrated_menu=menu,baseline_suite_with_diagnostic_firmware=menu,
report_sha256=hashlib.sha256(b).hexdigest(),runtime_identities=(profile/'.runtime.sha256').read_text().splitlines())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
