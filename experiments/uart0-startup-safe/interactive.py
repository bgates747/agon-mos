"""Input-only SDL taps into a disposable review profile, plus updater usage."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path
from lease import assert_checkout
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--attempt',default='keys');a=p.parse_args()
assert a.attempt.isalnum()
b=a.build.resolve();out=b/a.attempt;out.mkdir(exist_ok=False)
receipt=json.loads((b/('uart0-startup-safe-'+a.attempt)/'prepared.json').read_text());profile=Path(receipt['profile']);r=profile/'runtime';fifo=out/'keys.fifo';os.mkfifo(fifo)
subprocess.run(['gcc','-Wall','-Wextra','-Werror','-shared','-fPIC',str(root/'experiments/uart0-suite/tests/keys.c'),'-ldl','-o',str(out/'keys.so')],check=True)
proc=None
try:
 with (out/'frontend.log').open('w') as log:
  assert_checkout()
  proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE='jit',LD_PRELOAD=str(out/'keys.so'),UART_SUITE_KEYS=str(fifo)),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  def wire():
   p=profile/'last-run/mos-to-vdp.bin';return p.read_bytes() if p.exists() else b''
  def wait(marker,seconds=60):
   end=time.monotonic()+seconds
   while time.monotonic()<end:
    if marker in wire():return
    assert proc.poll() is None,'Frontend exited';time.sleep(.1)
   raise TimeoutError(marker)
  wait(b'Choose:');fd=os.open(fifo,os.O_WRONLY)
  os.write(fd,b'#1');wait(b'END run=0001 PASS')
  time.sleep(.5);os.write(fd,b'#2');wait(b'END run=0002 PASS')
  time.sleep(.5);os.write(fd,b'#q');wait(b'UART0 STARTUP-SAFE MENU RETURN')
  # No firmware arguments, images or confirmation keys: upstream prints usage.
  # Official flash.bin is linked at B0000h, not the normal LOAD address.
  # Decimal 720896 allows ordinary SDL digit events without shifted symbols.
  time.sleep(.5);os.write(fd,b'%load flash.bin 720896\nrun 720896\n');wait(b'Usage: FLASH')
  time.sleep(.5);os.write(fd,b'%dir\n');wait(b'Directory: /uart0')
  assert b'Programming MOS firmware' not in wire() and b'Unlocking VDP updater' not in wire()
  os.close(fd)
finally:
 if proc and proc.poll() is None:
  for c in Path('/proc').glob('[0-9]*'):
   try:
    if os.getpgid(int(c.name))==proc.pid and (c/'exe').resolve()==r/'flexe-agon-emulator.bin':os.kill(int(c.name),signal.SIGTERM)
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 if (profile/'last-run').exists():
  import shutil
  shutil.copytree(profile/'last-run',out/'raw')
result=dict(passed=True,quick_tap_tests=[1,2],menu_return=True,upstream_flash_usage=True,CLI_after_updater=True,firmware_programming=False)
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
