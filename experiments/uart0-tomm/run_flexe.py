"""Finite leased run of staged private profiles; cleanup owned processes only."""
import json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'experiments/uart0-startup-safe'))
from lease import assert_checkout
b=(root/sys.argv[1]).resolve();profiles=json.loads((b/'profiles.json').read_text())['profiles'];results=[]
for row in profiles:
 p=Path(row['path']);art=p/'last-run';out=p/'results';out.mkdir();error=None;proc=None;began=time.monotonic()
 try:
  with (out/'frontend.log').open('w') as log:
   assert_checkout()
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=row['engine']),start_new_session=True)
   previous=0;last=began
   while time.monotonic()-began<180:
    f=art/'mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
    if len(wire)!=previous:previous=len(wire);last=time.monotonic()
    if b'TM001 CLI RETURN' in wire:break
    assert b'TM001 FAIL' not in wire,'Guest reports FAIL'
    assert proc.poll() is None,'Frontend exited before CLI marker'
    assert time.monotonic()-last<45,'No UART progress for45seconds'
    time.sleep(.1)
   else:raise TimeoutError('180second cell limit')
 except Exception as exc:error=repr(exc)
 finally:
  if proc and proc.poll() is None:
   expected=(p/'flexe-agon-emulator.bin').resolve()
   for child in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(child.name))==proc.pid and (child/'exe').resolve()==expected:os.kill(int(child.name),signal.SIGTERM)
    except (OSError,PermissionError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  if art.exists():shutil.copytree(art,out/'raw')
  reports=out/'reports';reports.mkdir()
  subprocess.run(['mcopy','-s','-i',str(p/'card.img'),'::/uart0/*',str(reports)],stdout=subprocess.DEVNULL,check=True)
  wire=(art/'mos-to-vdp.bin').read_bytes() if (art/'mos-to-vdp.bin').exists() else b''
  passed=error is None and wire.count(b'VERIFY8192 PASS')==6 and b'TM001 PASS' in wire
  result=dict(**row,passed=passed,error=error,verify_count=wire.count(b'VERIFY8192 PASS'),elapsed=time.monotonic()-began,physical=False)
  (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result)
  (b/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
