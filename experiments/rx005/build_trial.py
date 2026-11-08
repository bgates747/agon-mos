"""Freeze/build the RX-005 MOS and original fixture under an actual Pi lease."""
import argparse, hashlib, importlib.util, json, os, shlex, shutil, signal, subprocess, time, zlib
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for key in ['source','baseline','sdk','fixture','out']:p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--lease',required=True);a=p.parse_args()
py='/Agon/mystuff/agon-dev-env/.venv/bin/python';ctl='/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
source=a.source.resolve();base=a.baseline.resolve()/'source';sdk=a.sdk.resolve()
assert sha(sdk/'lib/libagon.a')=='04e340186590810dd490d01655b50baaca557b7764006598890e845e6fc1252c'
assert sha(base/'bin/mos.bin')=='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50'
changed=sorted(p.name for p in (source/'src').iterdir() if p.is_file()and(not(base/'src'/p.name).exists()or sha(p)!=sha(base/'src'/p.name)))
assert changed==['interrupts.asm','mos_api.asm','uart0_receive.asm'],changed
src=out/'mos';shutil.copytree(source,src,ignore=shutil.ignore_patterns('.git','obj','bin','*.o','__pycache__'))
app=out/'fixture';shutil.copytree(a.fixture,app,ignore=shutil.ignore_patterns('obj','bin','__pycache__','identity.h'))
manifest={str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()}
(out/'mos-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
commands=[]
def run(command,cwd,logname):
 subprocess.run([py,ctl,'assert-owner','--owner','agon-mos','--lease',a.lease],check=True,stdout=subprocess.DEVNULL)
 commands.append(dict(command=command,cwd=str(cwd),log=logname));t=time.monotonic()
 with(out/logname).open('w')as log:
  c=subprocess.Popen(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:rc=c.wait(timeout=180)
  except BaseException:
   try:os.killpg(c.pid,signal.SIGTERM);c.wait(timeout=5)
   except ProcessLookupError:pass
   except subprocess.TimeoutExpired:os.killpg(c.pid,signal.SIGKILL);c.wait()
   raise
 assert rc==0,(logname,rc)
 return time.monotonic()-t
elapsed=run(['make','-j1','AGONDEV_TOOLCHAIN='+str(sdk)],src,'mos-compile.log')
image=(src/'bin/mos.bin').read_bytes()
command=next(shlex.split(l)for l in(out/'mos-compile.log').read_text().splitlines()if '/ez80-none-elf-ld 'in l)
command[command.index('--oformat')+1]='elf32-z80';command[command.index('-o')+1]=str(out/'mos.elf')
command=[('-Map='+str(out/'mos.elf.map'))if x.startswith('-Map=')else x for x in command]
run(command,src,'mos-elf-link.log')
subprocess.run([str(sdk/'bin/ez80-none-elf-objcopy'),'-O','binary',str(out/'mos.elf'),str(out/'from-elf.bin')],check=True,timeout=30)
assert(out/'from-elf.bin').read_bytes()==image
text=subprocess.check_output([str(sdk/'bin/ez80-none-elf-nm'),'-n',str(out/'mos.elf')],text=True);symbols={}
for line in text.splitlines():
 f=line.split()
 if len(f)>=3:
  try:symbols[f[-1]]=int(f[0],16)
  except ValueError:pass
(out/'symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
checker=Path('/Agon/mystuff/eirene-mos/experiments/irq-startup/verify.py');spec=importlib.util.spec_from_file_location('irqcheck',checker);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
startup=m.verify(image,symbols)
# Every other compiled unit must match the exact donor, including startup/TX.
changed_objects=sorted(p.name for p in(src/'obj').glob('*.o')if not(base/'obj'/p.name).exists()or sha(p)!=sha(base/'obj'/p.name))
assert changed_objects==['interrupts.o','mos_api.o','uart0_receive.o'],changed_objects
assert sha(src/'obj/init.o')==sha(base/'obj/init.o')
assert sha(src/'obj/serial.o')==sha(base/'obj/serial.o')
identity=dict(mos_sha256=sha(src/'bin/mos.bin'),source=manifest,fixture={str(p.relative_to(app)):sha(p)for p in app.rglob('*')if p.is_file()})
build=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:16]
(app/'src/identity.h').write_text('#define RX_BUILD "'+build+'"\n#define RX_MOS_BYTES '+str(len(image))+'u\n#define RX_MOS_CRC '+hex(zlib.crc32(image))+'UL\n#define RX_KBVECTOR '+hex(symbols['_user_kbvector'])+'u\n')
app_elapsed=run(['make','-j1','AGONDEV_TOOLCHAIN='+str(sdk)],app,'fixture-compile.log')
result=dict(schema='RX005-trial-build-1',build=build,changed_sources=changed,changed_objects=changed_objects,mos_bytes=len(image),mos_sha256=sha(src/'bin/mos.bin'),mos_map_sha256=sha(src/'bin/mos.map'),mos_crc32=f'{zlib.crc32(image):08X}',mos_added_bytes=len(image)-(base/'bin/mos.bin').stat().st_size,startup=startup,added_bss=symbols['___bss_len']-2098,fixture_bytes=(app/'bin/test.bin').stat().st_size,fixture_sha256=sha(app/'bin/test.bin'),fixture_sources={str(p.relative_to(app)):sha(p)for p in app.rglob('*')if p.is_file()and'obj'not in p.parts and'bin'not in p.parts},commands=commands,mos_build_seconds=elapsed,app_build_seconds=app_elapsed)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
