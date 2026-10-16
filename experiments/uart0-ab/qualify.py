"""Actual VDP protocol qualification; emulator times do not prove silicon timing."""
import hashlib,json,os,signal,shutil,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];probe=sys.argv[2:]==['--probe'];p=root/('.emulator/uart0-ab-probe' if probe else '.emulator/uart0-ab-auto');app=p/'sdcard/uart0';art=p/'last-run'
engine=sys.argv[1];assert engine in ('jit','interp')
art.mkdir(exist_ok=True)
for f in [*app.glob('*.dat'),*art.iterdir()]:
 if f.is_file():f.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
base=root/('build/uart0-ab/evidence-probe-'+engine if probe else f'build/uart0-ab/evidence-{engine}')
base.mkdir(exist_ok=True)
if (base/'receipt.json').exists():
 old=base/'previous-qualified.json';shutil.copyfile(base/'receipt.json',old);(base/'receipt.json').unlink()
number=1
while (base/f'attempt-{number:03d}').exists():number+=1
dest=base/f'attempt-{number:03d}';dest.mkdir()
proc=None;start=time.monotonic();returned=False
try:
 with (art/'frontend.log').open('w') as log:
  proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while time.monotonic()-start<240:
   if probe and (app/'ab-stall.dat').exists():returned=True;break
   assert not (app/'ab-fail.dat').exists(),'Native fixture failure'
   tx=art/'mos-to-vdp.bin';data=tx.read_bytes() if tx.exists() else b''
   if b'UART0 AB MOS RETURN' in data:returned=True;break
   assert proc.poll() is None,'Emulator exited early'
   time.sleep(.1)
  assert returned,'Timed out without MOS return'
finally:
 if proc and proc.poll() is None:
  for f in Path('/proc').glob('[0-9]*'):
   try:
    if os.getpgid(int(f.name))==proc.pid and (f/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():os.kill(int(f.name),signal.SIGTERM)
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  proc.wait(timeout=10)
 (dest/'outcome.json').write_text(json.dumps(dict(returned_to_mos=returned,qualification_complete=False,elapsed_seconds=round(time.monotonic()-start,3)))+'\n')
 for f in [*art.iterdir(),*app.glob('*.dat')]:
  if f.is_file():shutil.copyfile(f,dest/f.name)
assert proc.returncode==0
if probe and (app/'ab-stall.dat').exists():
 print('Watchdog report:',(app/'ab-stall.dat').read_bytes().hex());sys.exit(0)
b=(app/'ab.dat').read_bytes();assert b[:8]==b'UAB1\x01\x1e\x10\x00' and len(b)==488
rows=[]
for n in range(30):
 r=b[8+n*16:24+n*16];u24=lambda i:int.from_bytes(r[i:i+3],'little')
 assert r[13]==0 and r[14:]==b'\0\0',r.hex()
 assert r[0]==n//10 and r[2]==n%2
 assert r[1]==((n%10)//2 if n//10%2==0 else 4-(n%10)//2)
 assert u24(3)>0
 rows.append(dict(repeat=r[0],mode=r[1],kind=r[2],ticks=u24(3),useful_work=u24(6),irqs=u24(9),late_feeds=r[12],rx_errors=r[13]))
stats=json.loads((art/'stats.json').read_text());uart=json.loads((art/'uart.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')) and uart['tx_drops']==uart['rx_overruns']==0
# Every uploaded timed packet must appear exactly and in the planned order.
tx=(art/'mos-to-vdp.bin').read_bytes();bulk=(root/'build/uart0-ab/native/bulk-packet.bin').read_bytes();pace=(root/'build/uart0-ab/native/pace-packet.bin').read_bytes()
assert tx.count(bulk)==45 and tx.count(pace)==900,(tx.count(bulk),tx.count(pace))
receipt=dict(engine=engine,elapsed_seconds=round(time.monotonic()-start,3),returned_to_mos=True,phases=30,wire_packets_verified=945,receiver_bytes_checked_per_phase=735,receiver_bulk_full_payload_verified=False,physical_qualification=False,rows=rows,backend=stats,uart=uart,runtime_identities=(p/'.runtime.sha256').read_text().splitlines())
receipt['artifact_directory']=str(dest.relative_to(root))
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(base/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
