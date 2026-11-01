"""Qualify a fresh startup-safe ZDS image/menu against actual ESP32 firmware."""
import argparse,hashlib,importlib.util,json,os,shutil,signal,subprocess,time
from pathlib import Path
from lease import assert_checkout
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('engine',choices=['jit','interp']);p.add_argument('--fixture',default='fixture2');p.add_argument('--attempt',required=True);p.add_argument('--wrong-rom',action='store_true');a=p.parse_args()
assert a.attempt.isalnum()
b=a.build.resolve();f=b/a.fixture;out=b/('flexe-'+a.engine+'-'+a.attempt);out.mkdir(exist_ok=False)
profile=root/'.emulator'/('uart0-startup-safe-'+a.engine+'-'+a.attempt);profile.mkdir(exist_ok=False);r=profile/'runtime';r.mkdir()
h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
old=root/'.emulator/uart0-race';vdp=root/'build/uart0-native/vdp-batch-fixed/.pio/build/esp32dev'
files={'flexe-agon-emulator.bin':old/'flexe-agon-emulator.bin','flexe-vdp.so':old/'flexe-vdp.so','mos_platform.bin':b/'MOS.bin','mos_platform.map':b/'MOS.map','esp32-firmware.bin':vdp/'firmware.bin','esp32-firmware.elf':vdp/'firmware.elf'}
assert h(files['flexe-agon-emulator.bin'])=='412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
assert h(files['flexe-vdp.so'])=='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
assert h(files['esp32-firmware.bin'])=='201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a'
for name,src in files.items():
 shutil.copyfile(src,r/name)
 if name!='flexe-agon-emulator.bin':(profile/name).symlink_to('runtime/'+name)
(r/'flexe-agon-emulator.bin').chmod(0o755)
if a.wrong_rom:
 # Valid runnable candidate, but a harmless changed unused byte alters its
 # fingerprint. The menu must reject it before any transport activation.
 raw=bytearray((r/'mos_platform.bin').read_bytes());raw.extend(b'\x5a');(r/'mos_platform.bin').write_bytes(raw)
(profile/'fab-agon-emulator.bin').symlink_to('runtime/flexe-agon-emulator.bin');(profile/'sdcard').mkdir()
card=out/'card.img'
with card.open('xb') as handle:handle.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(card)],check=True,stdout=subprocess.DEVNULL);subprocess.run(['mmd','-i',str(card),'::/uart0'],check=True)
def put(src,name):subprocess.run(['mcopy','-i',str(card),str(src),'::/'+name],check=True)
for name in ('test.bin','stress.bin','app.bin','checks.bin'):put(f/name,'uart0/'+name)
startup=out/'autoexec.txt';startup.write_bytes(b'CD /uart0\r\nLOAD test.bin\r\nRUN . 0\r\nECHO FIRST STOCK CLI RETURN\r\nLOAD test.bin\r\nRUN . 0\r\nDIR\r\nECHO STARTUP SAFE CAMPAIGN RETURN\r\n');put(startup,'autoexec.txt');(profile/'sdcard.img').symlink_to(card)
(profile/'.mos-release').write_text('ZDS II startup-safe UART experiment; not hardware approved\n')
(profile/'.mos-release.sha256').write_text(''.join(h(profile/name)+'  '+name+'\n' for name in ('mos_platform.bin','mos_platform.map')))
(profile/'.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
spec=importlib.util.spec_from_file_location('factory',root/'build/uart0-branding/canonical_setup.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
factory.write_profile_launcher(profile,strict_bespoke=True)
launcher=profile/'fab-agon-emulator';text=launcher.read_text();token='vdp_name="$(< "${profile_dir}/.bespoke-vdp-profile")"';assert text.count(token)==1
text=text.replace(token,'''export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
mkdir -p "$AGON_FLEXE_ARTIFACTS"
'''+token)
token='        --sdcard "${profile_dir}/sdcard" \\\n';assert text.count(token)==2;text=text.replace(token,token+'        --sdcard-img "${profile_dir}/sdcard.img" \\\n');launcher.write_text(text);factory.name_flexe_profile(profile)
assert not (profile/'fab-agon-emulator').exists() and not (profile/'fab-agon-emulator.bin').exists()
names=list(files)+['flexe-agon-emulator'];(profile/'.runtime.sha256').write_text(''.join(h(profile/name)+'  '+name+'\n' for name in names));subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
started=time.monotonic();proc=None;error=None;art=profile/'last-run'
try:
 with (out/'frontend.log').open('w') as log:
  assert_checkout()
  proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=a.engine),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  last=time.monotonic();previous=0
  while time.monotonic()-started<420:
   path=art/'mos-to-vdp.bin';wire=path.read_bytes() if path.exists() else b''
   if len(wire)!=previous:last=time.monotonic();previous=len(wire)
   if a.wrong_rom and b'FAIL: wrong MOS image' in wire:break
   assert b'UART0 STARTUP-SAFE SUITE FAIL' not in wire and b'UART0 STRESS FAIL' not in wire,'Fixture reports FAIL'
   assert b'Error executing autoexec' not in wire,'MOS command execution failed'
   if b'STARTUP SAFE CAMPAIGN RETURN' in wire:break
   assert proc.poll() is None,'Emulator exited early'
   assert time.monotonic()-last<120,'No progress for two minutes'
   time.sleep(.2)
  else:raise TimeoutError('Campaign exceeded seven minutes')
except Exception as exc:error=repr(exc)
finally:
 if proc and proc.poll() is None:
  for child in Path('/proc').glob('[0-9]*'):
   try:
    if os.getpgid(int(child.name))==proc.pid and (child/'exe').resolve()==r/'flexe-agon-emulator.bin':os.kill(int(child.name),signal.SIGTERM)
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  time.sleep(.2)
 if art.exists():shutil.copytree(art,out/'raw')
 reports=out/'reports';reports.mkdir();subprocess.run(['mcopy','-s','-i',str(card),'::/uart0/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
 (profile/'sdcard.img').unlink()
try:
 assert error is None,error
 wire=(out/'raw/mos-to-vdp.bin').read_bytes()
 if a.wrong_rom:
  assert b'FAIL: wrong MOS image' in wire and b'Explicitly enabled session' not in wire
  assert not list(reports.glob('R*.log'))
 else:
  assert wire.count(b'UART0 STARTUP-SAFE SUITE PASS')==2
  assert b'FIRST STOCK CLI RETURN' in wire and b'STARTUP SAFE CAMPAIGN RETURN' in wire
  for n in (1,2):
   report=(reports/f'R{n:04}.log').read_text()
   for marker in ('STOCK DISCOVERY PASS','ACTIVATION CLOSE PASS','STRESS AND STOCK RETURN PASS','APPLICATION EXIT STOCK RESTORE PASS',f'END run={n:04} PASS'):assert marker in report,(n,marker)
   data=(reports/f'S{n:04}.dat').read_bytes();assert len(data)==76
   for i in range(4):assert data[12+i*16+1:12+i*16+3]==bytes([32,32])
   assert len((reports/f'I{n:04}.dat').read_bytes())==21
   assert not (reports/f'G{n:04}.dat').exists() and not (reports/f'J{n:04}.dat').exists()
  journal=(reports/'runs.log').read_text();assert 'run=0001' in journal and 'run=0002' in journal
  for i in range(4):
   packet=(f/'stress'/f'packet{i}.bin').read_bytes();assert wire.count(packet)==2,('complete packet',i)
  checks=(f/'checks.bin').read_bytes()
  for off in range(0,len(checks),60):assert wire.count(checks[off:off+60])==8,('receiver comparison',off)
 stats=json.loads((out/'raw/stats.json').read_text());uart=json.loads((out/'raw/uart.json').read_text())
 assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
 assert uart['tx_drops']==uart['rx_overruns']==0
except Exception as exc:
 if error is None:error=repr(exc)
verified=error is None and not a.wrong_rom
result=dict(passed=error is None,error=error,engine=a.engine,MOS_sha256=h(b/'MOS.bin'),VDP_sha256=h(vdp/'firmware.bin'),menu_sha256=h(f/'test.bin'),elapsed_seconds=round(time.monotonic()-started,3),wrong_ROM_control=a.wrong_rom,actual_compiled_ESP32=True,receiver_bytes_compared=65536 if verified else 0,ordered_replies=256 if verified else 0,physical_qualification=False,human_review_passed=False,profile=str(profile))
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed'],error
