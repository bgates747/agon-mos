#!/usr/bin/env python3
"""Source/linked and abstract notification controls; NOT an ISA emulator."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def normalized(text):
    return '\n'.join(x.split(';',1)[0].strip().lower() for x in text.splitlines()
                     if x.split(';',1)[0].strip())

def source_contract(raw):
    s=normalized(raw)
    assert s.count('\ndi\n')==1
    entry=s.split('entry:\n',1)[1].split('begin_pass:',1)[0]
    assert entry.index('ld a,i\njp po,refused')<entry.index('\ndi\n')
    assert entry.index('ld a,mb')<entry.index('\ndi\n')
    assert entry.count('jr z,refused')==2
    assert 'ld ix,(ix+6)' in entry
    assert 'push ix\nld ix,0\nadd ix,sp\npush bc\npush de\npush hl' in entry
    begin=s.split('begin_pass:\n')[1].split('wait_pass:')[0]
    assert begin.index('ld (ix+0),a')<begin.index('ld a,(hl)')
    assert begin.count('ld a,(hl)')==4
    assert 'ld (ix+1),1\nld a,1\njr enabled_return' in begin
    wait=s.split('wait_pass:\n')[1].split('sleep_return:')[0]
    assert 'ld (ix+0)' not in wait
    assert wait.index('ld (ix+1),a')<wait.index('ld a,(ix+0)')
    assert wait.count('cp (ix+')==4 and wait.count('jr nz,work')==5
    restore='pop hl\npop de\npop bc\npop ix'
    assert s.split('sleep_return:\n')[1].split('work:')[0].strip()==restore+'\nld a,3\nei\nhalt\nret'
    assert s.split('enabled_return:\n')[1].split('refused:')[0].strip()==restore+'\nei\nret'
    assert s.split('refused:\n')[1].strip()=='xor a\n'+restore+'\nret'
    for bad in ('in0','out0','rst','reti','exx','ex af','ld mb','call ','djnz'):
        assert bad not in s,bad
    return True

def abstract_controls():
    """Independent API state model, not an interpreter for native instructions."""
    def fresh():return dict(pending=0,clock=9,token=0,valid=False,ready=0)
    def begin(s):s.update(pending=0,token=s['clock'],valid=True)
    def event(s,kind,notified=True):
        if kind=='clock':s['clock']+=1
        else:
            s['ready']+=1
            if notified:s['pending']=1
    def wait(s,*,iff=True,context=True,clock_pointer=True,mb0=True):
        if not (iff and context and clock_pointer and mb0 and s['valid']):
            return 'REFUSED',iff
        s['valid']=False
        return ('WORK' if s['pending'] or s['clock']!=s['token'] else 'HALTED'),True
    results=[]
    for producer in ('callback','clock'):
        for arrival in ('before_clear','during_service','after_poll','under_DI','EI_shadow','after_HALT'):
            s=fresh();pending_irq=False;serviced=False
            if arrival=='before_clear':event(s,producer)
            begin(s)
            if arrival=='before_clear':s['ready']=0;serviced=True
            if arrival in ('during_service','after_poll'):event(s,producer)
            if arrival in ('under_DI','EI_shadow','after_HALT'):pending_irq=True
            status,iff=wait(s)
            if status=='HALTED' and pending_irq:event(s,producer)
            assert iff and (serviced or status=='WORK' or pending_irq)
            results.append(dict(producer=producer,arrival=arrival,status=status))
    # Actual contract mutation counterexamples: post-poll clear loses a callback;
    # an unnotified non-clock producer cannot be covered by this contract.
    s=fresh();begin(s);event(s,'callback');s['pending']=0
    assert wait(s)[0]=='HALTED' and s['ready']==1
    s=fresh();begin(s);event(s,'callback',notified=False)
    assert wait(s)[0]=='HALTED' and s['ready']==1
    for changes in ({'iff':False},{'context':False},{'clock_pointer':False},{'mb0':False}):
        s=fresh();begin(s);before=s.copy();status,iff=wait(s,**changes)
        assert status=='REFUSED' and s==before and iff==changes.get('iff',True)
    s=fresh();assert wait(s)[0]=='REFUSED'
    s=fresh();begin(s);assert wait(s)[0]=='HALTED';assert wait(s)[0]=='REFUSED'
    s=fresh();begin(s);event(s,'callback');event(s,'callback')
    assert wait(s)[0]=='WORK' and s['ready']==2 and s['pending']==1
    s=fresh();begin(s);s['clock']+=0x1000000
    assert wait(s)[0]=='WORK'  # compare all four bytes, not only low byte
    return dict(interleavings=results,refusal_and_token_controls='PASS',
                post_poll_clear_and_missing_producer_counterexamples='EXPOSED',
                coalescing_and_no_progress_sleep='PASS',
                scope='Abstract API/interrupt publication transitions only; no executed eZ80 instruction, peripheral or HALT.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--build',type=Path,required=True);p.add_argument('--toolchain',type=Path,required=True)
    a=p.parse_args();s=(a.source/'src/aw_wait.s').read_text();source_contract(s)
    mutants={
      'missing-DI':s.replace('\n di\n','\n nop\n'),
      'missing-IFF-refusal':s.replace(' jp po,refused',' nop'),
      'clear-event-in-wait':s.replace('wait_pass:\n','wait_pass:\n ld (ix+0),a\n'),
      'EI-NOP-HALT':s.replace(' ei\n halt',' ei\n nop\n halt'),
      'HALT-before-EI':s.replace(' ei\n halt',' halt\n ei\n nop'),
      'refusal-enables-IRQ':s.replace('refused:\n','refused:\n ei\n'),
      'incomplete-clock':s.replace(' cp (ix+5)',' nop'),
      'lost-HL-restore':s.replace('sleep_return:\n pop hl','sleep_return:\n nop')}
    rejected=[]
    for name,bad in mutants.items():
        try:source_contract(bad)
        except (AssertionError,IndexError,ValueError):rejected.append(name)
        else:raise AssertionError('Source mutant escaped: '+name)
    tool=a.toolchain/'bin'
    nm=subprocess.check_output([str(tool/'ez80-none-elf-nm'),'-a',str(a.build/'aw_wait.elf')],text=True)
    sym={m[2]:int(m[1],16) for line in nm.splitlines() if(m:=re.match(r'^([0-9a-fA-F]+)\s+\S\s+(\S+)$',line))}
    data=(a.build/'aw_wait.bin').read_bytes();base=0x40000
    def at(label,n):return data[sym[label]-base:sym[label]-base+n]
    sleep=bytes.fromhex('e1 d1 c1 dd e1 3e03 fb76 c9')
    assert at('sleep_return',len(sleep))==sleep
    assert at('refused',7)==bytes.fromhex('af e1 d1 c1 dde1 c9')
    assert at('enabled_return',7)==bytes.fromhex('e1 d1 c1 dde1 fb c9')
    assert bytes.fromhex('ed57 e2')+sym['refused'].to_bytes(3,'little') in data
    dis=subprocess.check_output([str(tool/'ez80-none-elf-objdump'),'-d',str(a.build/'aw_wait.elf')],text=True)
    (a.build/'aw_wait.disassembly.txt').write_text(dis)
    rows=[]
    for line in dis.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*(\S+)\s*(.*)$',line)
        if m:rows.append((int(m[1],16),m[2],m[3]))
    assert any(op=='ld' and args.startswith('ix,(ix+') and
               re.search(r'ix\+(?:0x0*)?6\)',args) for _,op,args in rows),'Argument at IX+6 missing'
    def branch_target(address,op):
        # This installed objdump prints JR targets truncated to16 bits even
        # for ADL addresses. Use linked displacement bytes plus the actual PC.
        off=address-base
        if op=='jr':return address+2+int.from_bytes(data[off+1:off+2],'little',signed=True)
        return int.from_bytes(data[off+1:off+4],'little')
    for address,op,args in rows:
        assert op not in ('call','djnz','in0','out0','rst','reti','reti.lil'),(op,args)
        if op in ('jp','jr'):
            assert branch_target(address,op)>address,'Backward edge in bounded leaf'
    assert sum(op=='halt' for _,op,_ in rows)==1
    # The linked leaf has only forward branches. Count instructions in its
    # longest DI-through-EI path; this is NOT an eZ80 cycle calculation.
    byaddr={v[0]:i for i,v in enumerate(rows)};memo={}
    def masked_length(i):
        if i in memo:return memo[i]
        address,op,args=rows[i]
        if op in ('ei','ret'):return 1
        followers=[i+1]
        if op in ('jp','jr'):
            target=branch_target(address,op)
            followers=[byaddr[target]]+([i+1] if ',' in args else [])
        memo[i]=1+max(masked_length(j) for j in followers)
        return memo[i]
    max_masked=masked_length(next(i for i,v in enumerate(rows) if v[1]=='di'))
    # Linked mutations are checker controls, not executed faulty code.
    pos=sym['sleep_return']-base
    for name,index,value in [('HALT-to-NOP',8,0),('EI-to-DI',7,0xf3),('bad-restore',0,0)]:
        bad=bytearray(data);bad[pos+index]=value
        assert bad[pos:pos+len(sleep)]!=sleep,name
    probe_dis=subprocess.check_output([str(tool/'ez80-none-elf-objdump'),'-dr',str(a.build/'probe.o')],text=True)
    (a.build/'probe.disassembly.txt').write_text(probe_dis)
    assert '_aw_begin' in probe_dis and '_aw_wait' in probe_dis
    artifacts={x.name:{'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
               for x in a.build.iterdir() if x.is_file() and x.suffix in ('.o','.elf','.a','.bin')}
    result={'source_contract':'PASS','source_mutations_rejected':rejected,'linked_mutations_rejected':3,
            'linked_contract':'PASS','abstract_model':abstract_controls(),'artifacts':artifacts,
            'leaf_text_bytes':len(data),'state_bytes':9,'leaf_stack_bytes_above_entry_SP':12,
            'static_decoded_instructions':len(rows),'max_DI_through_EI_instructions':max_masked,'symbols':sym,
            'limits':'Source/linked shape and abstract protocol model only; no executed ISA/IFF/register/IRQ/HALT/peripheral, cycle count or physical proof.'}
    (a.build/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('source_contract','linked_contract','leaf_text_bytes','state_bytes','limits')}))

if __name__=='__main__':main()
