"""Actual native MOS ABI1.2 with compiled, RX-repaired diagnostic VDP.

Disposable FAT media, frozen legacy test clients, direct canonical Flexe
launchers. No SD deployment, hardware operation, GUI or emulator model change.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from validate import validate

project=Path(__file__).resolve().parents[2]
native=Path.home()/'Agon/mystuff/worktrees/uart-native-001/uart'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('engine',choices=('jit','interp'))
parser.add_argument('--attempt',required=True)
parser.add_argument('--mos-build',default='uart-008-branded')
parser.add_argument('--clients',default='clients-002')
parser.add_argument('--no-quiescence-control',action='store_true')
args=parser.parse_args()
engine=args.engine
assert args.attempt.isalnum(), 'Use an alphanumeric attempt identifier'
control=args.no_quiescence_control
build=project/'build/uart0-native'
out=build/('flexe-'+engine+'-'+args.attempt)
out.mkdir(exist_ok=False)
p=native/'.emulator'/('uart0-'+engine+'-'+args.attempt)
p.mkdir(parents=True,exist_ok=False)
r=p/'runtime';r.mkdir()
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
mos=native/'.build'/args.mos_build/'bin'
old=project/'.emulator/uart0-race'
esp=build/'vdp-batch-fixed/.pio/build/esp32dev'
files={'flexe-agon-emulator.bin':old/'flexe-agon-emulator.bin',
 'flexe-vdp.so':old/'flexe-vdp.so','mos_platform.bin':mos/'MOS.bin',
 'mos_platform.map':mos/'MOS.map','esp32-firmware.bin':esp/'firmware.bin',
 'esp32-firmware.elf':esp/'firmware.elf'}
assert h(files['flexe-agon-emulator.bin'])=='412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
assert h(files['flexe-vdp.so'])=='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
for name,src in files.items():
 shutil.copyfile(src,r/name)
 if name.endswith('.bin'):(r/name).chmod(0o755)
 if name!='flexe-agon-emulator.bin':(p/name).symlink_to('runtime/'+name)
(p/'fab-agon-emulator.bin').symlink_to('runtime/flexe-agon-emulator.bin')
(p/'sdcard').mkdir()
image=out/'card.img'
with image.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mmd','-i',str(image),'::/uart0'],check=True)
client=project/'build/uart0-batching/native'
def copyin(src,name):subprocess.run(['mcopy','-i',str(image),str(src),'::/'+name],check=True)
copyin(client/'test.bin','uart0/test.bin')
copyin(client/'checks.bin','uart0/checks.bin')
sizes=(1,) if control else (1,2,4,8,16)
for n in sizes:
 stem='stress1-no-quiescence' if control else f'stress{n}'
 copyin(native/'.build'/args.clients/(stem+'.bin'),f'uart0/stress{n}.bin')
startup=b'CD /uart0\r\n'
if not control:startup+=b'LOAD test.bin &80000\r\nRUN &80000\r\n'
for n in sizes:startup+=f'LOAD stress{n}.bin &80000\r\nRUN &80000\r\n'.encode()
startup+=b'ECHO NATIVE UART RETURN\r\n'
(out/'autoexec.txt').write_bytes(startup);copyin(out/'autoexec.txt','autoexec.txt')
(p/'sdcard.img').symlink_to(image)
(p/'.mos-release').write_text('Native experimental UART0 ABI1.2; foundation ab95feee\n')
(p/'.mos-release.sha256').write_text(''.join(h(p/n)+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')))
(p/'.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
factory_path=project/'build/uart0-branding/canonical_setup.py'
spec=importlib.util.spec_from_file_location('canonical',factory_path)
factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
factory.write_profile_launcher(p,strict_bespoke=True)
launcher=p/'fab-agon-emulator';text=launcher.read_text()
token='vdp_name="$(< "${profile_dir}/.bespoke-vdp-profile")"'
assert text.count(token)==1
text=text.replace(token,'''export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
mkdir -p "$AGON_FLEXE_ARTIFACTS"
'''+token)
token='        --sdcard "${profile_dir}/sdcard" \\\n'
assert text.count(token)==2
text=text.replace(token,token+'        --sdcard-img "${profile_dir}/sdcard.img" \\\n')
launcher.write_text(text)
factory.name_flexe_profile(p)
assert not (p/'fab-agon-emulator').exists() and not (p/'fab-agon-emulator.bin').exists()
names=[*files,'flexe-agon-emulator']
(p/'.runtime.sha256').write_text(''.join(h(p/n)+'  '+n+'\n' for n in names))
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
art=p/'last-run';started=time.monotonic();proc=None;error=None
try:
 env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
 with (out/'frontend.log').open('w') as log:
  proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  last_progress=time.monotonic();last_size=0
  while time.monotonic()-started<900:
   wire=art/'mos-to-vdp.bin';data=wire.read_bytes() if wire.exists() else b''
   if len(data)!=last_size:last_progress=time.monotonic();last_size=len(data)
   assert time.monotonic()-last_progress<120,'No wire progress for two minutes'
   assert control or b'Error executing autoexec' not in data,'Native autoexec failure'
   assert b'UART0 BATCH TRANSPORT FAIL' not in data,'Native CRC client failure'
   assert control or b'UART0 STRESS FAIL' not in data,'Native stress client failure'
   if control and b'UART0 STRESS FAIL' in data:break
   if b'NATIVE UART RETURN' in data:break
   assert proc.poll() is None,'Frontend exited early'
   time.sleep(.15)
  else:raise TimeoutError('Native UART campaign did not return')
except Exception as exc:error=repr(exc)
finally:
 if proc and proc.poll() is None:
  for f in Path('/proc').glob('[0-9]*'):
   try:
    if os.getpgid(int(f.name))==proc.pid and (f/'exe').resolve()==r/'flexe-agon-emulator.bin':os.kill(int(f.name),signal.SIGTERM)
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 if art.exists():
  for f in art.iterdir():
   if f.is_file():shutil.copyfile(f,out/f.name)
 reports=out/'reports';reports.mkdir()
 subprocess.run(['mcopy','-s','-i',str(image),'::/uart0/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
 (p/'sdcard.img').unlink()
try:
 assert error is None,error
 wire=(out/'mos-to-vdp.bin').read_bytes()
 assert b'Arthur - UART0 OTIRX EXPERIMENTAL ABI1.2' in wire
 if control:
  report=(reports/'fail1.dat').read_bytes()
  assert report[:12]==b'UART0ST1\x01\x01\x04\x01', 'Expected policy setter BUSY (1), not an open failure'
  assert b'UART0 STRESS FAIL' in wire
  print('Negative control reproduced premature policy setter BUSY status1.')
except Exception as exc:
 if error is None:error=repr(exc)
try:
 if control or error is not None:raise StopIteration
 validate(out,client)
except StopIteration:pass
except Exception as exc:
 if error is None:error=repr(exc)
receipt=dict(passed=error is None,error=error,engine=engine,elapsed_seconds=round(time.monotonic()-started,3),
 actual_native_MOS=True,ROM_sha256=h(mos/'MOS.bin'),actual_compiled_ESP32=True,VDP_sha256=h(esp/'firmware.bin'),
 no_quiescence_negative_control=control,
 CRC_payload_bytes_verified=40960 if error is None and not control else 0,
 receiver_final_bytes_compared=163840 if error is None and not control else 0,
 ordered_full_duplex_replies=640 if error is None and not control else 0,
 batch_sizes=list(sizes),actual_FatFS=True,hardware_qualified=False,human_review_passed=False,
 raw_history=str(out),profile=str(p))
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
assert error is None,error
