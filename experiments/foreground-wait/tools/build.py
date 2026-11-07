#!/usr/bin/env python3
"""Finite FIFO-asserted native build, owned children joined before release."""
import argparse,importlib.util,json,os,signal,subprocess,time
from pathlib import Path

ENV=Path('/Agon/mystuff/agon-dev-env');PY=ENV/'.venv/bin/python'
LEASE=ENV/'cross-agent/pi5-workloads/pi5_lease.py'

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--toolchain',type=Path,required=True)
    p.add_argument('--lease',required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('guard',a.source.parent/'uart0-rfc-retry/build_pair.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    def ctl(*args):return subprocess.check_output([str(PY),str(LEASE),*args],text=True)
    ctl('assert-owner','--owner','agon-mos','--lease',a.lease)
    stop=[];steps=[];started=time.monotonic()
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,lambda s,f:stop.append(s))
    def run(name,cmd):
        ctl('assert-owner','--owner','agon-mos','--lease',a.lease)
        step={'name':name,'argv':cmd};steps.append(step);child=None;t=time.monotonic()
        try:
            sample=g.sensors()
            assert sample['temperature_c'] is not None and sample['temperature_c']<80 and sample['available_bytes']>=512*1024**2,sample
            with (a.output/(name+'.log')).open('x') as log:
                child=subprocess.Popen(['nice','-n','10',*cmd],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                while child.poll() is None:
                    s=g.sensors()
                    if stop or time.monotonic()-t>120 or time.monotonic()-started>300:raise RuntimeError('finite build stop')
                    if s['temperature_c'] is None or s['temperature_c']>=80 or s['available_bytes']<512*1024**2:raise RuntimeError('resource stop')
                    time.sleep(.25)
                step['returncode']=child.returncode
                if child.returncode:raise RuntimeError(name+' failed; retained log')
                if g.peers(child.pid):raise RuntimeError('Owned descendants still live')
        finally:
            if child:
                if g.peers(child.pid):
                    for sig in (signal.SIGTERM,signal.SIGKILL):
                        try:os.killpg(child.pid,sig)
                        except ProcessLookupError:pass
                        try:child.wait(timeout=2)
                        except subprocess.TimeoutExpired:pass
                        if not g.peers(child.pid):break
                child.wait();step['remaining_live']=g.peers(child.pid)
                if step['remaining_live']:raise RuntimeError('Owned children not joined')
            step['seconds']=time.monotonic()-t
            (a.output/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
    tool=a.toolchain/'bin';b=a.output;s=a.source
    try:
        run('assemble',[str(tool/'ez80-none-elf-as'),'-march=ez80+full',str(s/'src/aw_wait.s'),'-o',str(b/'aw_wait.o')])
        run('C-ABI-probe',[str(tool/'ez80-none-elf-clang'),'-target','ez80-none-elf','-mllvm','-z80-gas-style','-mllvm','-z80-print-zero-offset','-Wa,-march=ez80+full','-Oz','-nostdinc','-I'+str(a.toolchain/'include'),'-I'+str(s/'include'),'-c',str(s/'tests/probe.c'),'-o',str(b/'probe.o')])
        run('archive',[str(tool/'ez80-none-elf-ar'),'rcs',str(b/'libaw_wait.a'),str(b/'aw_wait.o')])
        run('probe-link',[str(tool/'ez80-none-elf-ld'),'-Ttext=0x040000','--entry=_bind_probe',str(b/'probe.o'),'-L'+str(b),'-law_wait','-L'+str(a.toolchain/'lib'),'-lagon','-o',str(b/'probe.elf')])
        run('link',[str(tool/'ez80-none-elf-ld'),'-Ttext=0x040000','--entry=_aw_begin',str(b/'aw_wait.o'),'-Map='+str(b/'aw_wait.map'),'-o',str(b/'aw_wait.elf')])
        run('raw',[str(tool/'ez80-none-elf-objcopy'),'-O','binary',str(b/'aw_wait.elf'),str(b/'aw_wait.bin')])
        run('controls',[str(PY),str(s/'tools/check.py'),'--source',str(s),'--build',str(b),'--toolchain',str(a.toolchain)])
    finally:
        if not any(v.get('remaining_live') for v in steps):
            (b/'release.json').write_text(ctl('release','--owner','agon-mos','--lease',a.lease,'--work-stopped','--cleanup-complete'))
    print(json.dumps({'passed':True,'seconds':time.monotonic()-started,'output':str(b)}))

if __name__=='__main__':main()
