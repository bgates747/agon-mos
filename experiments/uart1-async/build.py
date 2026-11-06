# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,hashlib,json,os,signal,subprocess,time,sys,shutil
args=argparse.ArgumentParser(description='Finite U1-001 host/native build only; requires an actual compiler checkout')
args.add_argument('--lease',required=True);args.add_argument('--out',type=Path,required=True);args.add_argument('--generation',type=int,required=True)
args.add_argument('--toolchain',type=Path,default=Path('/Agon/mystuff/eirene-mos/build/rc003/toolchain'))
a=args.parse_args()
root=Path(__file__).resolve().parents[2];src=root/'experiments/uart1-async';out=a.out.resolve();tool=a.toolchain.resolve();out.mkdir(parents=True,exist_ok=False)
lease=a.lease;start=time.monotonic();steps=[]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assertcmd=['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py','assert-owner','--owner','agon-mos','--lease',lease]
source={str(p.relative_to(src)):h(p) for p in sorted(src.rglob('*')) if p.is_file()}
shutil.copytree(src,out/'source');native=out/'native';(native/'src').mkdir(parents=True)
shutil.copytree(src/'include',native/'include')
for p in (src/'src').iterdir():shutil.copyfile(p,native/'src'/p.name)
shutil.copyfile(src/'fixture/main.c',native/'src/main.c')
(native/'Makefile').write_text('NAME = u1check\nRAM_START = 0x40000\nRAM_SIZE = 0x70000\nLDHAS_ARG_PROCESSING = 0\nLDHAS_EXIT_HANDLER = 0\ninclude $(AGONDEV_TOOLCHAIN)/config/makefile.inc\nCFLAGS += -std=c11 -Wall -Wextra -Werror -O2\n')
def run(name,args,cwd=root):
 subprocess.run(assertcmd,check=True,stdout=subprocess.DEVNULL)
 t=time.monotonic();p=None;code=None
 try:
  with (out/(name+'.log')).open('w') as f:
   p=subprocess.Popen(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   while p.poll() is None:
    temp=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text());avail=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
    if time.monotonic()-t>180 or time.monotonic()-start>600 or temp>=80000 or avail<524288:raise RuntimeError('finite build resource stop')
    time.sleep(.1)
   code=p.returncode
   if code:raise RuntimeError(name+' failed; original log retained')
 finally:
  if p:
   try:os.killpg(p.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   if p.poll() is None:
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
  steps.append(dict(name=name,exit=code,seconds=time.monotonic()-t))
try:
 run('host-build',['cc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(src/'include'),str(src/'src/u1_tx.c'),str(src/'tests/tx.c'),'-o',str(out/'host-test')])
 run('host-test',[str(out/'host-test')])
 run('native-build',['make','AGONDEV_TOOLCHAIN='+str(tool)],native)
 run('native-library',[str(tool/'bin/ez80-none-elf-ar'),'rcs',str(out/'libu1.a'),str(native/'obj/u1_tx.o'),str(native/'obj/u1_emit.o')])
 run('native-disassembly',[str(tool/'bin/ez80-none-elf-objdump'),'-d',str(native/'obj/u1_emit.o')])
 run('native-size',[str(tool/'bin/ez80-none-elf-size'),str(native/'obj/u1_tx.o'),str(native/'obj/u1_emit.o')])
 info=dict(passed=True,source=source,steps=steps,seconds=time.monotonic()-start,lease=lease,generation=a.generation,host_checks_only=True,native_guest_executed=False,hardware=False,firmware_changed=False,binary=dict(path=str(native/'bin/u1check.bin'),bytes=(native/'bin/u1check.bin').stat().st_size,sha256=h(native/'bin/u1check.bin')),library_sha256=h(out/'libu1.a'),libagon_sha256=h(tool/'lib/libagon.a'))
except Exception as e:
 info=dict(passed=False,error=str(e),steps=steps,source=source,seconds=time.monotonic()-start,generation=a.generation,native_guest_executed=False,hardware=False)
(out/'result.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2));sys.exit(0 if info['passed'] else 1)
