#!/usr/bin/env python3
"""Finite native paired build with actual FIFO assertion and owned cleanup."""
from pathlib import Path
import argparse, json, os, signal, subprocess, sys, time

ENV = Path('/Agon/mystuff/agon-dev-env')
PY = ENV/'.venv/bin/python'
LEASE = ENV/'cross-agent/pi5-workloads/pi5_lease.py'

def peers(pgid):
    found=[]
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            v=p.read_text().rsplit(') ',1)[1].split()
            if int(v[2])==pgid and v[0]!='Z':found.append(int(p.parent.name))
        except (OSError,ValueError,IndexError):pass
    return found

def sensors():
    available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines()
                       if s.startswith('MemAvailable:')))*1024
    temps=[int(p.read_text())/1000 for p in Path('/sys/class/thermal').glob('thermal_zone*/temp')]
    return {'available_bytes':available,'temperature_c':max(temps) if temps else None}

def main():
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True)
    p.add_argument('--toolchain',type=Path,required=True);p.add_argument('--lease',required=True)
    a=p.parse_args();out=a.pair/'checks';out.mkdir(exist_ok=False)
    started=time.monotonic();steps=[];stop=[]
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,lambda s,f:stop.append(s))
    def control(*args):
        return subprocess.run([str(PY),str(LEASE),*args],text=True,capture_output=True,check=True).stdout
    control('assert-owner','--owner','agon-mos','--lease',a.lease)
    def run(label,cmd,cwd):
        control('assert-owner','--owner','agon-mos','--lease',a.lease)
        s=sensors();assert s['available_bytes']>=512*1024**2 and (s['temperature_c'] or 0)<80,s
        proc=None;step={'label':label,'argv':cmd,'cwd':str(cwd),'initial':s};steps.append(step)
        began=time.monotonic()
        try:
            with (out/(label+'.log')).open('x') as log:
                proc=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                while proc.poll() is None:
                    s=sensors()
                    if stop or time.monotonic()-began>180 or time.monotonic()-started>600:
                        raise RuntimeError('Owned finite build stopped')
                    if s['available_bytes']<512*1024**2 or (s['temperature_c'] or 0)>=80:
                        raise RuntimeError(f'Resource stop: {s}')
                    time.sleep(.25)
                step['returncode']=proc.returncode
                if proc.returncode:raise RuntimeError(label+' failed; inspect retained log')
                if peers(proc.pid):raise RuntimeError('Live owned descendants after root exit')
        finally:
            if proc:
                if peers(proc.pid):
                    try:os.killpg(proc.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                    try:proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:pass
                    if peers(proc.pid):
                        try:os.killpg(proc.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                proc.wait()
                for _ in range(20):
                    if not peers(proc.pid):break
                    time.sleep(.05)
                step['remaining_live']=peers(proc.pid)
                if step['remaining_live']:raise RuntimeError('Owned cleanup incomplete')
            step['seconds']=time.monotonic()-began
            (out/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
    try:
        for label in ('original','candidate'):
            run(label,['make','-j1','AGONDEV_TOOLCHAIN='+str(a.toolchain)],a.pair/label)
    finally:
        # No next workload begins while our owned process group is alive.
        if not any(s.get('remaining_live') for s in steps):
            (out/'release.json').write_text(control('release','--owner','agon-mos',
                '--lease',a.lease,'--work-stopped','--cleanup-complete'))
    print(json.dumps({'paired_build_passed':True,'seconds':time.monotonic()-started,'checks':str(out)}))

if __name__=='__main__':main()
