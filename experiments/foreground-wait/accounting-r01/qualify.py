#!/usr/bin/env python3
"""Finite native object/link inspection only; never executes the target ISA."""
import argparse, hashlib, importlib.util, json, os, re, signal, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ENV = ROOT.parent / 'agon-dev-env'
PY = ENV / '.venv/bin/python'
LEASE = ENV / 'cross-agent/pi5-workloads/pi5_lease.py'
TOOL = ROOT.parent / 'agon-extender/agents/pingo-callback/tools/agondev'
OWNER = ROOT.parent / 'agon-extender/agents/net004/cpu-accounting-r01'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value): p.write_text(json.dumps(value, indent=2)+'\n')

def inspect(raw, syms):
    base = syms['_aw_begin']
    def at(label, want):
        i=syms[label]-base
        assert raw[i:i+len(want)] == want, label
    call=lambda name:b'\xcd'+syms[name].to_bytes(3,'little')
    restore=bytes.fromhex('e1d1c1dde1')
    at('sleep_return', b'\x3e\x06'+call('_agon_cpu_entry')+restore+
       bytes.fromhex('3e03fb76f53e86')+call('_agon_cpu_foreground')+bytes.fromhex('f1c9'))
    at('work', b'\x3e\x07'+call('_agon_cpu_entry')+bytes.fromhex('3e021801'))
    at('refused', b'\xaf'+restore+b'\xc9')
    at('enabled_return', restore+bytes.fromhex('fbc9'))
    at('refused_enabled', b'\xaf')
    assert bytes.fromhex('ed57e2')+syms['refused'].to_bytes(3,'little') in raw
    # Original MB and first NULL refusals must widen only in ON.
    assert bytes.fromhex('ed6eb7c2')+syms['refused'].to_bytes(3,'little') in raw
    assert bytes.fromhex('ed5228') in raw  # final short branch retained
    begin=raw[syms['begin_pass']-base:syms['wait_pass']-base]
    assert begin[:1]==b'\xaf' and begin[-4:-2]==bytes.fromhex('3e01')
    assert b'\xcd' not in begin
    assert raw[:5]==bytes.fromhex('3e011801af')
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--lease',required=True);a=p.parse_args();out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('guards',ROOT/'experiments/uart0-rfc-retry/build_pair.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    stop=[];steps=[];started=time.monotonic()
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,lambda s,f:stop.append(s))
    def ctl(*args):return subprocess.check_output([str(PY),str(LEASE),*args],text=True)
    def own():
        ctl('assert-owner','--owner','agon-mos','--lease',a.lease)
        assert not stop and time.monotonic()-started<300,'Whole-tranche stop'
    def run(name,argv):
        own();child=None;t=time.monotonic();step=dict(name=name,argv=list(map(str,argv)));steps.append(step)
        try:
            sample=g.sensors();assert sample['temperature_c'] is not None and sample['temperature_c']<80 and sample['available_bytes']>=512*1024**2,sample
            with (out/(name+'.log')).open('x') as log:
                child=subprocess.Popen(['nice','-n','10',*map(str,argv)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                while child.poll() is None:
                    sample=g.sensors()
                    assert not stop and time.monotonic()-t<120 and time.monotonic()-started<300
                    assert sample['temperature_c'] is not None and sample['temperature_c']<80 and sample['available_bytes']>=512*1024**2,sample
                    time.sleep(.1)
                step['returncode']=child.returncode
                assert child.returncode==0, name+' failed; retain first failure, no retry'
        finally:
            if child:
                for sig in (signal.SIGTERM,signal.SIGKILL):
                    if not g.peers(child.pid):break
                    try:os.killpg(child.pid,sig)
                    except ProcessLookupError:pass
                    try:child.wait(timeout=2)
                    except subprocess.TimeoutExpired:pass
                child.wait();step['remaining_live']=g.peers(child.pid)
                assert not step['remaining_live']
            step['seconds']=time.monotonic()-t;save(out/'steps.json',steps)
    tool=TOOL/'bin';baseline=ROOT/'experiments/foreground-wait'
    try:
        own()
        pins=json.loads((HERE/'source-pins.json').read_text())['inputs']
        for pin in pins:
            src=Path(pin['path']);assert src.stat().st_size==pin['bytes'] and digest(src)==pin['sha256'],str(src)
        manifest= json.loads((OWNER/'manifest.json').read_text())
        for pin in manifest['files']:
            if pin['path'].endswith('/qualification-r03/app.elf'):
                assert digest(Path(pin['path']))==pin['sha256']
                break
        else:raise AssertionError('Owner qualified app identity absent')
        objects=[]
        for name in ('accounting.o','accounting-c.o','provider.o','provider-c.o'):
            src=OWNER/'qualification-r03'/name; dst=out/name
            dst.write_bytes(src.read_bytes());objects.append(dst)
            pins.append(dict(path=str(src),bytes=src.stat().st_size,sha256=digest(src)))
        save(out/'actual-inputs.json',pins)
        for label,src,defs in [('original',baseline/'src/aw_wait.s',[]),('undefined',HERE/'aw_wait.s',[]),('off',HERE/'aw_wait.s',['--defsym','AW_CPU_ACCOUNTING=0']),('on',HERE/'aw_wait.s',['--defsym','AW_CPU_ACCOUNTING=1'])]:
            obj=out/(label+'.o');elf=out/(label+'.elf')
            run(label+'-assemble',[tool/'ez80-none-elf-as','-march=ez80+full',*defs,src,'-o',obj])
            run(label+'-link',[tool/'ez80-none-elf-ld','-Ttext=0x40000','--entry=_aw_begin','-Map='+str(out/(label+'.map')),obj,* (objects if label=='on' else []),'-L'+str(TOOL/'lib'),'-lagon','-o',elf])
            run(label+'-raw',[tool/'ez80-none-elf-objcopy','-O','binary',elf,out/(label+'.bin')])
            run(label+'-listing',[tool/'ez80-none-elf-objdump','-dr',elf])
            run(label+'-symbols',[tool/'ez80-none-elf-nm','-an',elf])
        original=(out/'original.bin').read_bytes()
        assert original==(out/'undefined.bin').read_bytes()==(out/'off.bin').read_bytes()
        assert original==(ROOT/'build/u1-wait-r01/native-r02/aw_wait.bin').read_bytes()
        nm=(out/'on-symbols.log').read_text()
        syms={x[2]:int(x[0],16) for line in nm.splitlines() if len(x:=line.split())==3 and re.fullmatch('[0-9a-fA-F]+',x[0])}
        raw=(out/'on.bin').read_bytes();extent=syms['refused']-syms['_aw_begin']+7;leaf=raw[:extent]
        assert extent==len(original)+24
        inspect(leaf,syms)
        # Real linked recorder entry/foreground save/restore, no stub HALT or recorder.
        start=syms['_agon_cpu_entry']-0x40000
        assert raw[start]==raw[start+4]==0xc3
        marker=int.from_bytes(raw[start+1:start+4],'little')-0x40000
        assert raw[marker:marker+16]==bytes.fromhex('f5c5d5e5dde5fde508f5d9c5d5e5d908')
        assert bytes.fromhex('08d9e1d1c1d9f108fde1dde1e1d1c1f1c9') in raw[marker:]
        fg=syms['_agon_cpu_foreground']-0x40000
        assert raw[fg:fg+7]==bytes.fromhex('f5c547ed57f3f5')
        assert '_agon_rxdiag_claim' in syms and '_agon_rxdiag_retire' in syms
        variants={}
        def replace(name,before,after):
            assert before in leaf,name
            variants[name]=leaf.replace(before,after,1)
        call=lambda n:b'\xcd'+syms[n].to_bytes(3,'little')
        replace('broken-EI-HALT',bytes.fromhex('fb76'),bytes.fromhex('fb00'))
        replace('wrong-work-event',b'\x3e\x07'+call('_agon_cpu_entry'),b'\x3e\x06'+call('_agon_cpu_entry'))
        replace('wrong-halt-event',b'\x3e\x06'+call('_agon_cpu_entry'),b'\x3e\x07'+call('_agon_cpu_entry'))
        replace('wrong-return-IFF-wrapper',call('_agon_cpu_foreground'),call('_agon_cpu_entry'))
        replace('lost-return-AF',bytes.fromhex('f1c9'),bytes.fromhex('00c9'))
        replace('wrong-work-result',bytes.fromhex('3e021801'),bytes.fromhex('3e011801'))
        replace('lost-HL-restore',bytes.fromhex('e1d1c1dde1'),bytes.fromhex('00d1c1dde1'))
        i=syms['refused']-0x40000;bad=bytearray(leaf);bad[i]=0xfb;variants['refusal-enables-IRQ']=bytes(bad)
        rejected=[]
        for name,bad in variants.items():
            try:inspect(bad,syms)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Broken linked image escaped: '+name)
        # Reuse exact established baseline controls and real C ABI probe.
        check=out/'baseline';check.mkdir()
        for dst,src in [('aw_wait.elf',out/'original.elf'),('aw_wait.bin',out/'original.bin'),('probe.o',ROOT/'build/u1-wait-r01/native-r02/probe.o')]:
            (check/dst).write_bytes(src.read_bytes())
        run('baseline-controls',[PY,baseline/'tools/check.py','--source',baseline,'--build',check,'--toolchain',TOOL])
        run('on-C-ABI-probe-link',[tool/'ez80-none-elf-ld','-Ttext=0x40000','--entry=_bind_probe',check/'probe.o',out/'on.o',*objects,'-L'+str(TOOL/'lib'),'-lagon','-o',out/'probe-on.elf'])
        run('on-relocations',[tool/'ez80-none-elf-objdump','-dr',out/'on.o'])
        run('on-size',[tool/'ez80-none-elf-size',out/'on.o',out/'on.elf'])
        artifacts={x.name:dict(bytes=x.stat().st_size,sha256=digest(x)) for x in out.iterdir() if x.is_file() and x.suffix in ('.o','.elf','.bin')}
        save(out/'result.json',dict(passed=True,baseline_bytes=len(original),on_leaf_bytes=extent,leaf_delta=extent-len(original),off_exact=True,linked_mutations_rejected=rejected,artifacts=artifacts,limits='Native assembly/link/source shape only; no executed ISA, register/IFF/IRQ/HALT/timer or hardware proof; no fitting firmware or app integration selected.'))
    finally:
        if not any(x.get('remaining_live') for x in steps):
            (out/'release.json').write_text(ctl('release','--owner','agon-mos','--lease',a.lease,'--work-stopped','--cleanup-complete'))

if __name__=='__main__':main()
