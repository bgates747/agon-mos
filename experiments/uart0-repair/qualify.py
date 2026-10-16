"""Execute actual compiled firmware and MOS FatFS through profile launchers."""
import argparse,hashlib,importlib.util,json,os,shutil,signal,subprocess,time
from pathlib import Path
from analyze import analyze
from profile import prepare_profile,root,b

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('variant',choices=('before','fixed','candidate','original'))
parser.add_argument('--engine',choices=('jit','interp'),default='jit')
parser.add_argument('--case',choices=('native','menu','campaign'),default='native')
parser.add_argument('--control',choices=('badcrc','noend','wrong-variant','wrong-candidate'))
a=parser.parse_args();assert not(a.variant=='candidate' and a.case!='campaign')
name=f'checks-{a.variant}-{a.engine}-{a.case}'+('-'+a.control if a.control else '')
parent=b/name;parent.mkdir(parents=True,exist_ok=True);number=1
while (parent/f'attempt-{number:03d}').exists():number+=1
dest=parent/f'attempt-{number:03d}';dest.mkdir()
image=dest/'card.img'
with image.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mmd','-i',str(image),'::/uart0'],check=True)
def copyin(source,name):subprocess.run(['mcopy','-o','-i',str(image),str(source),'::/'+name],check=True)
base=root/'build/uart0-race/hardware-return-002';old=json.loads((base/'manifest.json').read_text())
for f in base.iterdir():
    if f.suffix in ('.bin','.dat','.log') and not f.name.startswith(('vdp-','mos-')):
        if f.name in old['files']:assert hashlib.sha256(f.read_bytes()).hexdigest()==old['files'][f.name]['sha256']
        copyin(f,'uart0/'+f.name)
copyin(b/'test.bin','uart0/test.bin')
native=bytearray((b/'native/repair.bin').read_bytes());assert native[64:73]==b'MOS\0\1URF1' and native[137]==255
expected=int(a.variant=='fixed');native[137]=1-expected if a.control=='wrong-variant' else expected
payload=bytes(((n*157+7)%254)+1 for n in range(4096))+b'\0'
if a.control in ('badcrc','noend'):
    assert native.count(payload)==1;native[native.index(payload)+(4096 if a.control=='noend' else 0)]^=1
(dest/'repair.bin').write_bytes(native);copyin(dest/'repair.bin','uart0/repair.bin')
cfg=dest/'suite.cfg';cfg.write_text('board=Oryx matched receiver synchronization regression\nvdp_label='+a.variant+' compiled firmware\nvdp_flash=0\nphysical_receiver=0\n');copyin(cfg,'uart0/suite.cfg')
run=b'RUN &80000\r\n' if a.case=='native' else b'RUN . candidate\r\n' if a.case=='campaign' else b'RUN\r\n'
load=b'LOAD repair.bin &80000\r\n' if a.case=='native' else b'LOAD test.bin\r\n'
(dest/'autoexec.txt').write_bytes(b'CD /uart0\r\n'+load+run+b'ECHO RXFIX RETURN\r\n');copyin(dest/'autoexec.txt','autoexec.txt')
seed=hashlib.sha256(image.read_bytes()).hexdigest();p=prepare_profile(a.variant,image,a.engine)
art=p/'last-run';art.mkdir(exist_ok=True)
for f in art.iterdir():
    if f.is_file():f.unlink()
keys=dest/'keys';keys.write_bytes(b'')
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=a.engine)
if a.case=='menu':env.update(LD_PRELOAD=str(root/'build/uart0-ui/keys.so'),UART_SUITE_KEYS=str(keys))
started=time.monotonic();process=None;cursor=0;error=None;result=None
def wire():
    f=art/'mos-to-vdp.bin';return f.read_bytes() if f.exists() else b''
def wait(marker,limit=180):
    global cursor
    until=time.monotonic()+limit
    while time.monotonic()<until:
        data=wire();at=data.find(marker,cursor)
        if at>=0:cursor=at+len(marker);return
        if process.poll() is not None:raise RuntimeError('Frontend exited')
        time.sleep(.05)
    raise TimeoutError(f'{marker!r}: {wire()[-240:]!r}')
def key(value):
    with keys.open('ab') as f:f.write(value)
try:
    with (dest/'frontend.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        if a.case=='menu':
            wait(b'Press a choice key:');key(b'#9');wait(b'VDP flashing is unavailable in this emulator profile.');key(b'#5')
            wait(b'Run 0011: SKIP');wait(b'Press a choice key:');key(b'#8');wait(b'Q Back\r\nChoose:');key(b'#6' if expected else b'#5')
            wait(b'Run 0012: PENDING');wait(b'Press any key for menu.');key(b'# ')
            wait(b'Press a choice key:');key(b'#q');wait(b'UART0 SUITE RETURN PASS')
        wait(b'RXFIX RETURN',300 if a.case=='campaign' else 180)
except Exception as e:error=repr(e)
finally:
    if process and process.poll() is None:
        for proc in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(proc.name))==process.pid and (proc/'exe').resolve()==p/'runtime/flexe-agon-emulator.bin':os.kill(int(proc.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    for f in art.iterdir():
        if f.is_file():shutil.copyfile(f,dest/f.name)
    reports=dest/'reports';reports.mkdir()
    subprocess.run(['mcopy','-s','-i',str(image),'::/uart0/*',str(reports)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    # Never leave an automatic run's evidence image available for mutation.
    (p/'sdcard.img').unlink()
try:
    assert error is None,error
    stats=json.loads((dest/'stats.json').read_text());uart=json.loads((dest/'uart.json').read_text())
    assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')) and uart['tx_drops']==uart['rx_overruns']==0
    if a.case=='campaign':
        text=(reports/'R0011.log').read_text()
        if a.control=='wrong-candidate':assert 'TEST 15 SKIP' in text and 'TEST 15 PASS' not in text
        else:
            for t in (1,6,2,3,10,15):assert f'TEST {t} PASS' in text
            assert 'VDP=RX-sync-candidate' in text and 'RECOVERY_SCOPE RX-sync-candidate' in text
            spec=importlib.util.spec_from_file_location('recovery_reader',root/'experiments/uart0-recovery/analyze.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
            result=reader.analyze((reports/'Y0011.dat').read_bytes());assert result['campaign_passed']
            assert (reports/'Y0011.dat').read_bytes()==(reports/'Z0011.dat').read_bytes()
            assert 'CANDIDATE COMPATIBILITY PASS' in wire().decode(errors='ignore')
    else:
        report=reports/('U0012.dat' if a.case=='menu' else 'race.dat');result=analyze(report.read_bytes())
        if a.control=='wrong-variant' or a.variant=='original':
            assert result['stage']==3 and not result['completed'] and payload not in wire()
        elif a.control:
            assert result['protocol_complete'] and not result['regression_passed'] and not all(c['integrity_passed'] for c in result['cases'])
        else:
            assert result['regression_passed'] and result['receiver_fixed']==bool(expected)
            progress=reports/('O0012.dat' if a.case=='menu' else 'race-step.dat');assert progress.read_bytes()==report.read_bytes()
            for mode in (0,1):assert bytes([23,0,0xe6,0,mode,0])+payload in wire()
        if a.case=='menu':
            t=14 if expected else 13;assert f'TEST {t} PENDING' in (reports/'R0012.log').read_text()
            assert 'FLASH_HANDOFF' not in (reports/'R0011.log').read_text()
            for f in base.iterdir():
                if f.suffix in ('.dat','.log') and f.name!='runs.log':assert (reports/f.name).read_bytes()==f.read_bytes()
            assert (reports/'runs.log').read_bytes().startswith((base/'runs.log').read_bytes())
except Exception as e:
    if error is None:error=repr(e)
receipt=dict(passed=error is None,error=error,variant=a.variant,engine=a.engine,case=a.case,control=a.control,
    control_rejected=bool(a.control) and error is None,actual_MOS_FatFS=True,hostfs_disabled=True,
    physical_test_performed=False,physical_repair_verified=False,result=result,
    elapsed_seconds=round(time.monotonic()-started,3),seed_image_sha256=seed,
    menu_sha256=hashlib.sha256((b/'test.bin').read_bytes()).hexdigest(),native_sha256=hashlib.sha256((b/'native/repair.bin').read_bytes()).hexdigest(),
    firmware_sha256=hashlib.sha256((p/'esp32-firmware.bin').read_bytes()).hexdigest(),runtime_identities=(p/'.runtime.sha256').read_text().splitlines())
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if error:print(json.dumps(receipt,indent=2),flush=True);raise RuntimeError(error)
(parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('result','runtime_identities')},indent=2),flush=True)
