"""Check the native Console8 menu package through actual FAT media in Flexe."""
import hashlib,importlib.util,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-native';engine=sys.argv[1]
assert engine in ('jit','interp')
native=Path.home()/'Agon/mystuff/worktrees/uart-native-001/uart'
out=b/('hardware-menu-'+engine);out.mkdir(exist_ok=False)
p=native/'.emulator'/('uart0-hardware-menu-'+engine)
shutil.copytree(native/'.emulator/uart0-review1',p,symlinks=True,ignore=shutil.ignore_patterns('last-run','sdcard.img','.runtime.sha256'))
vdp=root/'build/uart0-repair/candidate/.pio/build/esp32dev'
for suffix in ('bin','elf'):shutil.copyfile(vdp/('firmware.'+suffix),p/'runtime'/('esp32-firmware.'+suffix))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(vdp/'firmware.bin')==sha(b/'console8-native/vdp-rx-fixed.bin')
image=out/'card.img'
with image.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mmd','-i',str(image),'::/uart0'],check=True)
for name in ('test.bin','stress.bin','checks.bin','app.bin','short.bin','bench.bin'):
 subprocess.run(['mcopy','-i',str(image),str(b/'console8-native'/name),'::/uart0/'+name],check=True)
(out/'suite.cfg').write_text('board=Native menu software check\nvdp_label=RX sync candidate\nvdp_flash=0\nphysical_receiver=0\n')
subprocess.run(['mcopy','-i',str(image),str(out/'suite.cfg'),'::/uart0/suite.cfg'],check=True)
startup=b'CD /uart0\r\n'
for n in (3,3,6,1,2):startup+=f'LOAD test.bin\r\nRUN . {n}\r\n'.encode()
startup+=b'ECHO NATIVE HARDWARE MENU RETURN\r\n'
(out/'autoexec.txt').write_bytes(startup)
subprocess.run(['mcopy','-i',str(image),str(out/'autoexec.txt'),'::/autoexec.txt'],check=True)
(p/'sdcard.img').symlink_to(image)
spec=importlib.util.spec_from_file_location('canonical',root/'build/uart0-branding/canonical_setup.py')
factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory);factory.name_flexe_profile(p)
names=['flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf']
(p/'.runtime.sha256').write_text(''.join(sha(p/n)+'  '+n+'\n' for n in names))
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
start=time.monotonic();proc=None;error=None
try:
 with (out/'frontend.log').open('w') as log:
  proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while time.monotonic()-start<600:
   f=p/'last-run/mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
   assert b'Error executing autoexec' not in wire and b'UART0 STRESS FAIL' not in wire,'Menu campaign failed'
   if b'NATIVE HARDWARE MENU RETURN' in wire:break
   assert proc.poll() is None;time.sleep(.2)
  else:raise TimeoutError('Native menu campaign timed out')
except Exception as exc:error=repr(exc)
finally:
 if proc and proc.poll() is None:
  for child in Path('/proc').glob('[0-9]*'):
   try:
    if os.getpgid(int(child.name))==proc.pid and (child/'exe').resolve()==p/'runtime/flexe-agon-emulator.bin':os.kill(int(child.name),signal.SIGTERM)
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  deadline=time.monotonic()+10
  while not (p/'last-run/stats.json').exists() and time.monotonic()<deadline:time.sleep(.05)
 if (p/'last-run').exists():shutil.copytree(p/'last-run',out/'raw')
 reports=out/'reports';reports.mkdir()
 subprocess.run(['mcopy','-s','-i',str(image),'::/uart0/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
 (p/'sdcard.img').unlink()
if error:raise AssertionError(error)
wire=(out/'raw/mos-to-vdp.bin').read_bytes()
assert wire.count(b'UART0 STRESS FIXTURE PASS')==2
for i,test in enumerate((3,3,6,1,2),1):
 log=(reports/f'R{i:04}.log').read_text()
 assert f'TEST {test} PASS' in log and f'END run={i:04} PASS' in log,(i,log)
for i in (1,2):
 data=(reports/f'S{i:04}.dat').read_bytes();assert len(data)==76 and data[:12]==b'UART0ST1\x01\0\x04\0'
 for n in range(4):
  row=data[12+n*16:28+n*16]
  assert row[1]==row[2]==32 and row[10]==row[12]==0 and row[13]==47 and row[14:16]==b'\xff\xff'
stats=json.loads((out/'raw/stats.json').read_text());uart=json.loads((out/'raw/uart.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
assert uart['tx_drops']==uart['rx_overruns']==0
receipt=dict(passed=True,engine=engine,elapsed_seconds=round(time.monotonic()-start,3),tests=[3,3,6,1,2],sequential_reports_verified=True,actual_FatFS=True,
 menu_sha256=sha(b/'console8-native/test.bin'),stress_sha256=sha(b/'console8-native/stress.bin'),VDP_sha256=sha(vdp/'firmware.bin'),hardware_qualified=False)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
