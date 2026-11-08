"""Finite native donor build; assert actual Pi compiler ownership before launch."""
import argparse, hashlib, importlib.util, json, os, re, shlex, signal, subprocess, tarfile, time
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lease',required=True)
p.add_argument('--source',type=Path,required=True)
p.add_argument('--sdk',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
py='/Agon/mystuff/agon-dev-env/.venv/bin/python'
ctl='/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.sdk/'lib/libagon.a')=='04e340186590810dd490d01655b50baaca557b7764006598890e845e6fc1252c'
pin='97311c437093e416342a6c836cf9914f2ced027d'
assert subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()==pin
archive=out/'source.tar'
with archive.open('wb') as f:subprocess.run(['git','-C',str(a.source),'archive',pin],stdout=f,check=True)
src=out/'source';src.mkdir()
with tarfile.open(archive) as t:t.extractall(src,filter='data')
subprocess.run([py,ctl,'assert-owner','--owner','agon-mos','--lease',a.lease],check=True,stdout=subprocess.DEVNULL)
t0=time.monotonic()
with (out/'compile.log').open('w') as log:
 child=subprocess.Popen(['make','-j1','AGONDEV_TOOLCHAIN='+str(a.sdk.resolve())],cwd=src,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:rc=child.wait(timeout=180)
 except BaseException:
  try:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=5)
  except ProcessLookupError:pass
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  raise
assert rc==0,rc
image=(src/'bin/mos.bin').read_bytes()
assert hashlib.sha256(image).hexdigest()=='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50','Donor differs from published RC3'
# The flat linker map omits local symbols. Relink an ELF with identical inputs,
# then require byte parity before using its complete symbol table.
command=next(shlex.split(l) for l in (out/'compile.log').read_text().splitlines() if '/ez80-none-elf-ld ' in l)
command[command.index('--oformat')+1]='elf32-z80'
command[command.index('-o')+1]=str(out/'mos.elf')
command=[('-Map='+str(out/'mos.elf.map')) if x.startswith('-Map=') else x for x in command]
subprocess.run(command,cwd=src,check=True,timeout=30)
subprocess.run([str(a.sdk/'bin/ez80-none-elf-objcopy'),'-O','binary',str(out/'mos.elf'),str(out/'from-elf.bin')],check=True,timeout=30)
assert (out/'from-elf.bin').read_bytes()==image
text=subprocess.check_output([str(a.sdk/'bin/ez80-none-elf-nm'),'-n',str(out/'mos.elf')],text=True)
s={}
for line in text.splitlines():
 fields=line.split()
 if len(fields)>=3:
  try:s[fields[-1]]=int(fields[0],16)
  except ValueError:pass
(out/'symbols.json').write_text(json.dumps(s,indent=2)+'\n')
check=Path('/Agon/mystuff/eirene-mos/experiments/irq-startup/verify.py')
spec=importlib.util.spec_from_file_location('irqcheck',check);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
startup=mod.verify(image,s)
info=dict(schema='RX005-baseline-1',commit=pin,source_tar_sha256=sha(archive),bytes=len(image),sha256=hashlib.sha256(image).hexdigest(),map_sha256=sha(src/'bin/mos.map'),startup=startup,elapsed_seconds=time.monotonic()-t0,sdk=str(a.sdk.resolve()),libagon_sha256=sha(a.sdk/'lib/libagon.a'),toolchain={n:sha(a.sdk/'bin'/n) for n in ['ez80-none-elf-clang','ez80-none-elf-as','ez80-none-elf-ld']},startup_checker_sha256=sha(check))
(out/'result.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
