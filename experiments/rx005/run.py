"""Oryx only: finite leased RX005 end-to-end cells, stop at first failure."""
from pathlib import Path
import argparse,importlib.util,json,os,shlex,shutil,signal,subprocess,time,hashlib
p=argparse.ArgumentParser(description=__doc__);p.add_argument('profiles',type=Path);p.add_argument('--lease',required=True);a=p.parse_args()
root=a.profiles.resolve().parent;config=json.loads(a.profiles.read_text());results=[]
spec=importlib.util.spec_from_file_location('wire',Path(__file__).with_name('check_wire.py'));oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
injector=Path('/home/smith/Agon/mystuff/agon-6502/build/dsk003/sdl_keys.so')
assert hashlib.sha256(injector.read_bytes()).hexdigest()=='e223b8f55958b78629717a5b957232dbf60fa8606801aeb8263f00bfca8ad37a'
sdl_digest='6c68aecb2057c78c02cb694edc691a81f92bda2b186e6e8ad156d79638c19048'
assert hashlib.sha256(Path('/usr/lib/x86_64-linux-gnu/libSDL3.so.0').read_bytes()).hexdigest()==sdl_digest
def ownership():
 cmd=['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/vdplet-rollout/oryx_lease.py','assert-owner','--owner','agon-mos','--lease',a.lease]
 subprocess.run(['ssh','-o','BatchMode=yes','raspberrypi',shlex.join(cmd)],check=True,stdout=subprocess.DEVNULL)
def health():
 boosts=[int(f.read_text()) for f in Path('/sys/devices/system/cpu/cpufreq').glob('policy*/boost')]
 assert boosts and not any(boosts),'CPU boost must remain off'
 temps=[int(f.read_text())/1000 for f in Path('/sys/class/hwmon').glob('hwmon*/temp*_input') if (f.parent/'name').read_text().strip()=='k10temp']
 assert temps and max(temps)<80,temps
 memory=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))
 assert memory>=512*1024,memory
 return {'boost':boosts,'temperatures_C':temps,'available_KiB':memory}
def children(group):
 found=[]
 for item in Path('/proc').glob('[0-9]*'):
  try:
   pid=int(item.name)
   if os.getpgid(pid)==group and (item/'stat').read_text().split(') ',1)[1][0]!='Z':found.append(pid)
  except (OSError,ValueError):pass
 return found
for row in config['profiles']:
 profile=Path(row['path']);out=profile/'results';out.mkdir(exist_ok=False);proc=None;fd=None;error=None;injected=False;mapped=False;failure_seen=None;baseline_saved=False;start=time.monotonic();last=start;size=0
 try:
  host=health()
  assert hashlib.sha256((profile/'card.img').read_bytes()).hexdigest()==row['initial_card_sha256'],'initial card changed'
  (out/'initial-host-health.json').write_text(json.dumps(host,indent=2)+'\n')
  for pin in ('.runtime.sha256','.mos-release.sha256'):subprocess.run(['sha256sum','--check','--status',pin],cwd=profile,check=True)
  assert not list((profile/'last-run').iterdir()),'nonempty artifacts'
  fifo=out/'keys.fifo';os.mkfifo(fifo);fd=os.open(fifo,os.O_RDWR|os.O_NONBLOCK)
  with (out/'frontend.log').open('w') as log:
   ownership()
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',LD_PRELOAD=str(injector),AGON_TEST_KEY_FIFO=str(fifo),MOS_UART_STATS=str(profile/'last-run/uart.json')))
   nexthealth=0
   while time.monotonic()-start<180:
    now=time.monotonic()
    if now>=nexthealth:health();nexthealth=now+3
    if not mapped:
     for pid in children(proc.pid):
      try:
       if (Path('/proc')/str(pid)/'exe').resolve()!=(profile/'flexe-agon-emulator.bin').resolve():continue
       maps=(Path('/proc')/str(pid)/'maps').read_text()
       libraries={Path(line.split()[-1])for line in maps.splitlines()if '/libSDL3.so.' in line}
       if libraries:
        assert all(hashlib.sha256(lib.read_bytes()).hexdigest()==sdl_digest for lib in libraries),'wrong mapped SDL'
        (out/'mapped-libraries.txt').write_text(maps);mapped=True
      except FileNotFoundError:pass
    trace=profile/'last-run/mos-to-vdp.bin';wire=trace.read_bytes() if trace.exists() else b''
    if len(wire)!=size:size=len(wire);last=now
    if b'RX005 UART BEFORE127 BASELINE' in wire and not baseline_saved and b'RX005 UART SNAPSHOT' not in wire:
     shutil.copyfile(profile/'last-run/uart.json',out/'uart-before127.json');baseline_saved=True
    if b'RX005 KEY READY: press and release A once.' in wire and not injected:
     time.sleep(.2);assert os.write(fd,bytes([4,1]))==2;time.sleep(.15);assert os.write(fd,bytes([4,0]))==2
     injected=True;(out/'key-events.json').write_text(json.dumps({'scancode':4,'events':['down','up'],'source':'SDL_PollEvent FIFO','after_ready':True})+'\n')
    if b'RX005 CLI RETURN' in wire:
     assert b'RX005 SUITE PASS' in wire and b'RX005 RETURN PASS' in wire and injected and mapped;break
    if b'RX005 SUITE FAIL' in wire:
     if failure_seen is None:failure_seen=now
     if b'RX005 FAILURE LOG CLOSED; storage remains live' in wire or now-failure_seen>=5:raise AssertionError('guest failure; see raw wire/report')
    if any(s in wire for s in (b'RX005 REFUSED',b'Error executing autoexec',b'Guru meditation',b'RST $38 panic')):raise AssertionError('guest refusal/panic; see raw wire')
    if proc.poll() is not None:raise AssertionError('frontend exited early')
    if now-last>45:raise TimeoutError('45s without UART progress')
    time.sleep(.05)
   else:raise TimeoutError('180s cell bound')
 except Exception as exc:error=repr(exc)
 finally:
  if fd is not None:os.close(fd)
  if proc:
   # Signal actual raw frontend first; wrapper exit alone is not cleanup.
   expected=(profile/'flexe-agon-emulator.bin').resolve()
   for pid in children(proc.pid):
    try:
     if (Path('/proc')/str(pid)/'exe').resolve()==expected:os.kill(pid,signal.SIGTERM)
    except OSError:pass
   deadline=time.monotonic()+12
   while children(proc.pid) and time.monotonic()<deadline:time.sleep(.1)
   if children(proc.pid):os.killpg(proc.pid,signal.SIGKILL)
   proc.wait(timeout=10)
   assert not children(proc.pid),'owned processes survived cleanup'
  if (profile/'last-run').exists():shutil.copytree(profile/'last-run',out/'raw')
  (out/'reports').mkdir()
  subprocess.run(['mcopy','-s','-i',str(profile/'card.img'),'::/rx005/*',str(out/'reports')],check=True,stdout=subprocess.DEVNULL)
 try:
  if error:raise AssertionError(error)
  report=(out/'reports/R0001.log').read_text()
  proof=oracle.verify((out/'raw/vdp-to-mos.bin').read_bytes(),report)
  assert (out/'reports/next.txt').read_text().strip()=='2'
  stats=json.loads((out/'raw/stats.json').read_text())
  assert stats['engine']==row['engine'] and stats['coherence']=='upstream-write-watch' and stats['isync'] is None,stats
  assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')),stats
  assert b'RX005 UART SNAPSHOT lctl=03 ier=01 issued=1' in (out/'raw/mos-to-vdp.bin').read_bytes()
  uart=json.loads((out/'raw/uart.json').read_text())
  assert not uart['tx_drops'] and not uart['rx_overruns'],uart
  proof['uart_counter_scope']='Lifetime through fixture final same-IER write; startup included'
  delivered=out/'raw/vdp-to-mos-delivered.bin'
  end=proof['wire_bytes_through_end']
  assert delivered.read_bytes()[:end]==(out/'raw/vdp-to-mos.bin').read_bytes()[:end],'undelivered fixture prefix'
  proof['wire_scope']='Through ordered GP34 cleanup; later CLI tail retained but not qualified'
  (out/'wire-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 except Exception as exc:
  if error is None:error=repr(exc)
 result={**row,'passed':error is None,'error':error,'elapsed_seconds':time.monotonic()-start,'injected':injected,'mapped_SDL_verified':mapped,'physical':False}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result);(root/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
 if error:raise SystemExit('Stopped at first failure; preserve evidence')
