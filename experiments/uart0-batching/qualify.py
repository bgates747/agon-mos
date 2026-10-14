"""Full receiver integrity and full-duplex checks; no hardware CTS-margin claim."""
import hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-batching';native=build/'native'
profile=root/'.emulator/uart0-batching';app=profile/'sdcard/uart0';artifacts=profile/'last-run'
engine=sys.argv[1];assert engine in ('jit','interp')
control=sys.argv[2] if len(sys.argv)>2 else None;assert control in (None,'crc','noend')
for p in Path('/proc').glob('[0-9]*'):
    try:
        if (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Batching profile is active')
    except (FileNotFoundError,PermissionError):pass
artifacts.mkdir(exist_ok=True)
dest=build/('evidence-'+engine+('-'+control if control else ''))
if dest.exists():
    history=build/'history';history.mkdir(exist_ok=True)
    index=1
    while (history/f'{dest.name}-{index:03d}').exists():index+=1
    shutil.move(dest,history/f'{dest.name}-{index:03d}')
for p in [*artifacts.iterdir(),*app.glob('*.dat')]:
    if p.is_file():p.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
original=(app/'test.bin').read_bytes();pins=(profile/'.runtime.sha256').read_text()
if control:
    data=bytearray(original)
    if control=='crc':
        crc=json.loads((native/'expected.json').read_text())['payload_crc32'].to_bytes(4,'little')
        assert original.count(crc)==1;data[original.index(crc)]^=1
    else:
        tail=bytes(((n*157+7)%254)+1 for n in range(32,4096))+b'\0'
        assert original.count(tail)==1;data[original.index(tail)+len(tail)-1]=1
    (app/'test.bin').write_bytes(data)
    (profile/'.runtime.sha256').write_text(pins.replace(hashlib.sha256(original).hexdigest()+'  sdcard/uart0/test.bin',hashlib.sha256(data).hexdigest()+'  sdcard/uart0/test.bin'))
process=None;started=time.monotonic();returned=False;rejected=False
try:
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
    with (artifacts/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=profile,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while time.monotonic()-started<300:
            p=artifacts/'mos-to-vdp.bin';wire=p.read_bytes() if p.exists() else b''
            if b'UART0 BATCH TRANSPORT FAIL' in wire:
                if control:rejected=True;break
                raise RuntimeError('Batch receiver test failed')
            if b'UART0 STRESS FAIL' in wire:raise RuntimeError('Full-duplex fixture failed')
            if b'UART0 BATCH CAMPAIGN RETURN' in wire:returned=True;break
            if process.poll() is not None:raise RuntimeError('Emulator exited early')
            time.sleep(.15)
        assert rejected if control else returned,'Timed out; passing earlier phases do not qualify a stall'
finally:
    if process and process.poll() is None:
        for p in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(p.name))==process.pid and (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():os.kill(int(p.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    dest=build/('evidence-'+engine+('-'+control if control else ''));dest.mkdir(exist_ok=True)
    for p in [*artifacts.iterdir(),*app.glob('*.dat')]:
        if p.is_file():shutil.copyfile(p,dest/p.name)
    (app/'test.bin').write_bytes(original);(profile/'.runtime.sha256').write_text(pins)
assert process.returncode==0
u32=lambda b,o:int.from_bytes(b[o:o+4],'little')
if control:
    report=(dest/'batch-fail.dat').read_bytes();assert len(report)==492 and report[:9]==b'UBTHOST1\x01' and report[9]==2
    row=report[12:60];expected=json.loads((native/'expected.json').read_text())
    if control=='crc':assert u32(row,36)==4096 and u32(row,40)==expected['payload_crc32']
    else:assert row[44]&4 and u32(row,36)==4097
    receipt=dict(engine=engine,control=control,rejected=True,elapsed_seconds=round(time.monotonic()-started,3),physical_qualification=False)
else:
    report=(dest/'batch.dat').read_bytes();assert len(report)==492 and report[:12]==b'UBTHOST1\x01\x00\x0a\x00'
    expected=json.loads((native/'expected.json').read_text());rows=[]
    for i,(n,hold) in enumerate(expected['cases']):
        row=report[12+i*48:60+i*48]
        assert row[:7]==b'URM1'+bytes([1,64,hold]);assert u32(row,36)==4096 and u32(row,40)==expected['payload_crc32']
        assert u32(row,12)==u32(row,24)==0 and row[44]==row[47]==0 and row[45]==1,row.hex()
        rows.append(dict(batch=n,pause_ms=hold,received=u32(row,36),crc32=f'{u32(row,40):08X}',restored=True))
    wire=(dest/'mos-to-vdp.bin').read_bytes();assert b'UART0 BATCH INTEGRITY PASS' in wire
    for n in (1,2,4,8,16):
        report=(dest/f'stress{n}.dat').read_bytes();assert len(report)==76 and report[:12]==b'UART0ST1\x01\x00\x04\x00'
        for i,pause in enumerate((0,1,4,8)):
            row=report[12+i*16:28+i*16];packet=(native/f'packet{i}.bin').read_bytes()
            assert row[0]==pause and row[1]==row[2]==32 and row[3]>0
            assert int.from_bytes(row[4:7],'little')==len(packet) and row[10]==row[12]==row[14]==row[15]==0 and row[13]==47
            assert wire.count(packet)==5,'Full-duplex wire mismatch'
    checks=(native/'checks.bin').read_bytes()
    for off in range(0,len(checks),60):assert wire.count(checks[off:off+60])==20,'Missing byte comparator'
    stats=json.loads((dest/'stats.json').read_text());uart=json.loads((dest/'uart.json').read_text())
    assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'));assert uart['tx_drops']==uart['rx_overruns']==0
    receipt=dict(engine=engine,elapsed_seconds=round(time.monotonic()-started,3),integrity_rows=rows,crc_payload_bytes=40960,
    receiver_bytes_compared=163840,ordered_full_duplex_replies=640,all_batch_sizes=[1,2,4,8,16],returned_to_mos=True,
    physical_qualification=False,known_receiver_race_cleared=False,graphical_instance_launched=False,
    runtime_identities=pins.splitlines(),backend=stats,uart=uart)
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
