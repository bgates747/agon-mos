"""Finite Oryx-only reset qualification; real compiled VDP, virtual FAT media."""
import argparse,hashlib,importlib.util,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path

root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'experiments/uart0-startup-safe'))
from lease import assert_checkout

p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--attempt',required=True);p.add_argument('--review',action='store_true');p.add_argument('--qualified-attempt',default='q004');a=p.parse_args()
assert a.attempt.isalnum() and a.qualified_attempt.isalnum()
b=a.build.resolve();f=b/'fixture';out=b/('qualification-'+a.attempt);out.mkdir(exist_ok=False)
h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
source=root/'.emulator/uart0-startup-safe-jit-final'
assert not (source/'sdcard.img').exists()
spec=importlib.util.spec_from_file_location('factory',root/'build/uart0-branding/canonical_setup.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
meta=json.loads((f/'metadata.json').read_text())
assert h(b/'MOS.bin')=='89ea8694194e0488337bf1dcbfa91e2b084b3afc75a9c3916f4acc9ae12aa42b'

def prepare(name,commands):
 profile=root/'.emulator'/('uart0-reset-'+a.attempt+'-'+name);assert not profile.exists()
 shutil.copytree(source,profile,symlinks=True,ignore=shutil.ignore_patterns('last-run','.runtime.sha256'))
 d=out/name;d.mkdir();card=d/'card.img'
 with card.open('xb') as handle:handle.truncate(32*1024*1024)
 subprocess.run(['mkfs.fat','-F','16',str(card)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['mmd','-i',str(card),'::/uart0'],check=True)
 for n in ('test.bin','stress.bin','app.bin','checks.bin'):subprocess.run(['mcopy','-i',str(card),str(f/n),'::/uart0/'+n],check=True)
 (profile/'sdcard.img').symlink_to(card);startup(card,d,commands)
 factory.name_flexe_profile(profile)
 assert not (profile/'fab-agon-emulator').exists() and not (profile/'fab-agon-emulator.bin').exists()
 pins(profile)
 return profile,card,d

def pins(profile):
 names=('flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf')
 assert h(profile/'esp32-firmware.bin')=='201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a'
 assert h(profile/'flexe-agon-emulator.bin')=='412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
 assert h(profile/'flexe-vdp.so')=='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
 (profile/'.runtime.sha256').write_text(''.join(h(profile/n)+'  '+n+'\n' for n in names))
 subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
 subprocess.run(['bash','-n','flexe-agon-emulator'],cwd=profile,check=True)

def startup(card,d,commands):
 text=d/'autoexec.txt';text.write_bytes(('CD /uart0\r\nLOAD test.bin\r\n'+commands).encode())
 subprocess.run(['mcopy','-o','-i',str(card),str(text),'::/autoexec.txt'],check=True)

def extract(card,d):
 d.mkdir();subprocess.run(['mcopy','-s','-i',str(card),'::/uart0/*',str(d)],check=True,stdout=subprocess.DEVNULL)

def phase(profile,card,d,engine,marker,kind='return',timeout=90):
 d.mkdir();art=profile/'last-run'
 if art.exists():shutil.rmtree(art)
 proc=None;wire=b'';error=None;stable_card=False;keys_sent=False;key_stage=0
 environment=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
 if kind in ('expiry','verifykeys'):
  fifo=d/'keys.fifo';os.mkfifo(fifo)
  helper=d/'keys.so';subprocess.run(['gcc','-Wall','-Wextra','-Werror','-shared','-fPIC',str(root/'experiments/uart0-suite/tests/keys.c'),'-ldl','-o',str(helper)],check=True)
  environment.update(LD_PRELOAD=str(helper),UART_SUITE_KEYS=str(fifo))
 try:
  with (d/'frontend.log').open('w') as log:
   assert_checkout()
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   end=min(time.monotonic()+timeout,started+600)
   while time.monotonic()<end:
    path=art/'mos-to-vdp.bin';wire=path.read_bytes() if path.exists() else b''
    assert proc.poll() is None,'Frontend exited before marker'
    if kind=='expiry' and not keys_sent and b'RESET WINDOW EXPIRED' in wire:
     fd=os.open(fifo,os.O_WRONLY);os.write(fd,b'#e');os.close(fd);keys_sent=True
    if kind=='verifykeys':
     trigger=(b'Choose:',b'come straight here? Y/N',b'UART0 RESET RECOVERY PASS')[min(key_stage,2)]
     if key_stage<3 and trigger in wire:
      fd=os.open(fifo,os.O_WRONLY);os.write(fd,(b'#7',b'#y',b'#q')[key_stage]);os.close(fd);key_stage+=1
    if marker in wire:
     if kind in ('active','halt'):
      # READY is issued only after every guest filesystem handle is closed.
      before=h(card);time.sleep(1);after=h(card);assert before==after,'SD changed after RESET NOW'
      stable_card=True
      if kind=='halt':
       again=path.read_bytes();time.sleep(.5);assert path.read_bytes()==again,'Controlled stop did not quiesce UART'
     break
    if b'RESET PREPARATION FAIL' in wire or b'Reset preparation failed' in wire:raise AssertionError('Preparation failed')
    time.sleep(.1)
   else:raise TimeoutError('Expected marker not reached')
 except Exception as exc:error=repr(exc)
 finally:
  if proc and proc.poll() is None:
   runtime=(profile/'runtime/flexe-agon-emulator.bin').resolve()
   for child in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(child.name))==proc.pid and (child/'exe').resolve()==runtime:os.kill(int(child.name),signal.SIGTERM)
    except (FileNotFoundError,PermissionError,ProcessLookupError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  if art.exists():shutil.copytree(art,d/'raw')
  extract(card,d/'reports')
 if error:raise AssertionError(error)
 wire=(d/'raw/mos-to-vdp.bin').read_bytes();stats=json.loads((d/'raw/stats.json').read_text());uart=json.loads((d/'raw/uart.json').read_text())
 assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
 assert uart['tx_drops']==uart['rx_overruns']==0
 (d/'receipt.json').write_text(json.dumps(dict(passed=True,engine=engine,kind=kind,SD_stable_after_READY=stable_card,emulator_stopped=True),indent=2)+'\n')
 return wire

def arm_record(path,state=1):
 raw=path.read_bytes();assert len(raw)==64 and raw[:8]==b'URST0001' and raw[9]==state
 assert raw[12:28].decode()==meta['build_id']
 import zlib
 assert int.from_bytes(raw[60:64],'little')==zlib.crc32(raw[:60])
 assert raw[35:38]==bytes([3,1,1])
 return raw

started=time.monotonic();results=[];pending_seed=None
try:
 if a.review:
  qualified=json.loads((b/('qualification-'+a.qualified_attempt)/'receipt.json').read_text())
  assert qualified['passed'] and qualified['menu_sha256']==h(f/'test.bin')
  profile,card,d=prepare('review','RUN .\r\n')
  text=d/'readme.txt';text.write_text('UART0 deliberate-reset fixture; same installed MOS/VDP.\r\n'
   '5 streams continuously; 6 stops the CPU partway through a VDP packet.\r\n'
   'Both save a pending record and close report files before RESET NOW.\r\n'
   'Only after RESET NOW: power the whole Console8 OFF/ON (emulator: close/reopen).\r\n'
   'Reopen test.bin, choose7 thenY to confirm you saw READY and performed reset.\r\n'
   'Expect UART0 RESET RECOVERY PASS; Q thenDIR checks ordinary CLI.\r\n'
   'Option5 expires after60seconds: do NOT reset; pressE to save EXPIRED, NOT PASS.\r\n'
   'Option6 is EXPECTED to stop. A stopped screen alone is NOT PASS.\r\n'
   'Runall excludes these reset tests. No new firmware flash required.\r\n')
  subprocess.run(['mcopy','-i',str(card),str(text),'::/uart0/readme.txt'],check=True)
  result=dict(prepared=True,profile=str(profile),card=str(card),stopped=True,automatic_activation=False,menu_sha256=h(f/'test.bin'),MOS_sha256=h(b/'MOS.bin'),human_review_passed=False,hardware_qualified=False)
  (d/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(0)
 for engine in ('jit','interp'):
  for mode in (5,6):
   name=f'{engine}-mode{mode}';profile,card,d=prepare(name,f'RUN . {mode}\r\n')
   marker=b'All SD files are CLOSED.'
   wire=phase(profile,card,d/'before-reset',engine,marker,'active' if mode==5 else 'halt')
   raw=arm_record(d/'before-reset/reports/reset.arm');assert raw[8]==mode
   # Count bytes in the first READY packet, including the known partial buffer write.
   title=b'RESET NOW - '+(b'SENDING CONTINUOUSLY' if mode==5 else b'CONTROLLED MID-PACKET STOP')
   start=wire.index(title)-1;remaining=wire[start:]
   if mode==6:
    header=bytes([23,0,0xa0,0xf2,0x6a,0,0,1]);data=remaining.index(header)+len(header)
    assert 0<len(remaining)-data<256,('Not stopped inside first256-byte body',len(remaining)-data)
   else:assert remaining.count(b'RESET NOW')>=2,'No sustained active sending'
   if pending_seed is None:pending_seed=raw
   startup(card,d,'RUN .\r\nDIR\r\nECHO RESET VERIFIED CLI\r\n')
   after=phase(profile,card,d/'after-reset',engine,b'RESET VERIFIED CLI',kind='verifykeys')
   final=arm_record(d/'after-reset/reports/reset.arm',3)
   assert final[8]==mode and final[10:28]==raw[10:28]
   report=(d/'after-reset/reports/R0001.log').read_text();assert 'END run=0001 RESET PASS' in report
   assert b'Directory: /uart0' in after and b'UART0 RESET RECOVERY PASS' in after
   results.append(dict(engine=engine,mode=mode,passed=True,partial_packet_proven=mode==6))
  # Runall remains the ordinary four-test campaign and never arms a reset.
  profile,card,d=prepare(engine+'-ordinary','RUN . 0\r\nECHO ORDINARY CLI RETURN\r\n')
  wire=phase(profile,card,d/'run',engine,b'ORDINARY CLI RETURN',timeout=120)
  assert b'UART0 STARTUP-SAFE SUITE PASS' in wire and b'RESET NOW' not in wire
  assert not (d/'run/reports/reset.arm').exists()
  results.append(dict(engine=engine,ordinary_tests=True,passed=True))
 # Negative controls prove a pending card record alone cannot manufacture PASS.
 for name,commands,seed,marker in (
  ('missing','RUN . 7y\r\n',None,b'RESET VERIFY REFUSED: no armed test.'),
  ('noreset','RUN . 2\r\nRUN . 7y\r\n',pending_seed,b'RESET VERIFY REFUSED: fresh disabled reset state is missing.'),
  ('corrupt','RUN . 7y\r\n',bytes(pending_seed[:-1])+bytes([pending_seed[-1]^1]),b'RESET VERIFY REFUSED: corrupt arm record.'),
 ):
  profile,card,d=prepare('negative-'+name,commands)
  if seed is not None:
   seedfile=d/'reset.arm';seedfile.write_bytes(seed);subprocess.run(['mcopy','-i',str(card),str(seedfile),'::/uart0/reset.arm'],check=True)
  wire=phase(profile,card,d/'run','jit',marker)
  assert b'UART0 RESET RECOVERY PASS' not in wire
  results.append(dict(negative_control=name,passed=True))
 profile,card,d=prepare('negative-wrongrom','RUN . 5\r\n')
 rom=profile/'mos_platform.bin';rom.write_bytes(rom.read_bytes()+b'\x5a')
 (profile/'.mos-release.sha256').write_text(''.join(h(profile/n)+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')));pins(profile)
 wire=phase(profile,card,d/'run','jit',b'FAIL: wrong MOS image; no activation.')
 assert not (d/'run/reports/reset.arm').exists() and not list((d/'run/reports').glob('R*.log'))
 results.append(dict(negative_control='wrong-ROM',passed=True))
 # No-reset expiry must be recorded as EXPIRED rather than success.
 profile,card,d=prepare('negative-expired','RUN . 5\r\n')
 phase(profile,card,d/'before','jit',b'RESET EXPIRY SAVED',kind='expiry',timeout=100)
 arm_record(d/'before/reports/reset.arm',2)
 startup(card,d,'RUN . 7y\r\n');wire=phase(profile,card,d/'verify','jit',b'RESET VERIFY REFUSED: run expired or already verified.')
 assert b'UART0 RESET RECOVERY PASS' not in wire
 results.append(dict(negative_control='expired',passed=True))
 receipt=dict(passed=True,results=results,elapsed_seconds=round(time.monotonic()-started,3),MOS_unchanged=True,MOS_sha256=h(b/'MOS.bin'),menu_sha256=h(f/'test.bin'),physical_hardware_test=False,human_review_passed=False)
except Exception as exc:
 receipt=dict(passed=False,error=repr(exc),results=results,elapsed_seconds=round(time.monotonic()-started,3),physical_hardware_test=False)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed'],receipt
