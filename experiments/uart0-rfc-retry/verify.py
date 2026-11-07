#!/usr/bin/env python3
"""Read-only source/linked structural proofs, NOT a guest or ISR execution."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, subprocess, zlib

def norm(s):
    return '\n'.join(re.sub(r'\s+',' ',x.split(';',1)[0].strip().lower())
                     for x in s.splitlines() if x.split(';',1)[0].strip())

DEFER='''in0 a,(UART0_IER)
and 0xfd
out0 (UART0_IER),a
ld a,1
ld (uart0_tx_retry_pending),a
pop af
ei
reti.lil'''
RETRY='''ld a,(uart0_tx_retry_pending)
or a
ret z
in0 a,(PD_DR)
tst a,8
ret nz
xor a
ld (uart0_tx_retry_pending),a
in0 a,(UART0_IER)
or 2
out0 (UART0_IER),a
ret'''

def source_checks(serial,irq,original,old_irq):
    s=norm(serial);old=norm(original);v=norm(irq);ov=norm(old_irq)
    assert not re.search(r'(?m)^(?:\.macro )?wait_cts$',s),'Unbounded async CTS macro remains'
    head=s.split('fill_uart0_tx_fifo:\n',1)[1].split('.last_fill:',1)[0]
    admit='in0 a,(pd_dr)\ntst a,8\njr nz,uart0_tx_defer\n'
    assert head.startswith(admit+'push bc\npush de\npush hl\n'),'CTS admission must precede all mutation/saves'
    d=s.split('uart0_tx_defer:\n',1)[1].split('uart0_async_retry:',1)[0].strip()
    assert d==norm(DEFER),'Deferred path changed state, return frame or IER mask'
    retry=s.split('uart0_async_retry:\n',1)[1].split('.bss',1)[0].strip()
    assert retry==norm(RETRY),'Retry must be bounded/inactive without I/O, preserve IER and only rearm'
    assert s.endswith('uart0_tx_retry_pending: .ds 1'),'Exactly one retry-state byte required'
    assert 'uart0_async_send:\nxor a\nld (uart0_tx_retry_pending),a\n' in s,'New submission must invalidate retry'
    final=s.split('.last_fill:\n',1)[1].split('uart0_tx_defer:',1)[0]
    assert 'xor a\nld (uart0_tx_retry_pending),a\ncall uart0_tx_callback' in final,'Final callback must see cleared retry'
    # The admitted transfer paths must otherwise be byte-for-byte donor source.
    new_fill=s.split('fill_uart0_tx_fifo:\n',1)[1].split('uart0_tx_defer:',1)[0].strip()
    new_fill=new_fill.removeprefix(admit).replace('xor a\nld (uart0_tx_retry_pending),a\n','')
    old_fill=old.split('fill_uart0_tx_fifo:\n',1)[1].replace('wait_cts\n','').strip()
    assert new_fill==old_fill,'Native donor count/copy/register/callback path altered'
    assert v.replace('xref uart0_async_retry\n','').replace('call uart0_async_retry\n','')==ov,'Other IRQ code changed'
    vb=v.split('_vblank_handler:',1)[1].split('_uart0_handler:',1)[0]
    assert vb.count('call uart0_async_retry')==1 and vb.index('call uart0_async_retry')<vb.index('pop hl'),'Retry outside VBlank save'
    assert s.count('otirx')==2,'Only donor copy paths may emit'
    # All 256 IER values: off preserves unrelated RX/other bits, on only sets TX.
    for ier in range(256):
        assert (ier&0xfd)&0xfd==ier&0xfd
        assert ((ier&0xfd)|2)&0xfd==ier&0xfd
    return {'source_contract':'PASS','IER_cases':256,'transfer_paths':'admitted donor source unchanged',
            'execution':'none; exact source/control-shape and bit algebra only'}

def map_symbols(text):
    return {m[2]:int(m[1],16) for line in text.splitlines()
            if (m:=re.match(r'^\s*(0x[0-9a-fA-F]+)\s+([A-Za-z_][\w.]*)\b',line))}

def local_symbols(root,obj,tool):
    text=(root/'bin/mos.map').read_text();result=map_symbols(text)
    bases={m[1]:int(m[2],16) for line in text.splitlines()
           if (m:=re.match(r'^ (\.\w+)\s+(0x[0-9a-fA-F]+)\s+0x[0-9a-fA-F]+\s+obj/'+re.escape(obj)+r'\.o$',line))}
    table=subprocess.check_output([str(tool/'bin/ez80-none-elf-objdump'),'-t',str(root/'obj'/f'{obj}.o')],text=True)
    for line in table.splitlines():
        words=line.split()
        if len(words)>=5 and re.fullmatch('[0-9a-fA-F]{8}',words[0]):
            for sec,base in bases.items():
                if sec in words:result[words[-1]]=base+int(words[0],16)
    return result

def verify(pair,tool,donor):
    original=(pair/'original/src/serial.asm').read_text();old_irq=(pair/'original/src/interrupts.asm').read_text()
    serial=(pair/'candidate/src/serial.asm').read_text();irq=(pair/'candidate/src/interrupts.asm').read_text()
    result=source_checks(serial,irq,original,old_irq)
    bad={
        'original-spinning-CTS':original,
        'mutate-count-before-admission':serial.replace('fill_uart0_tx_fifo:\n','fill_uart0_tx_fifo:\n ld (uart0_tx_data_count),hl\n',1),
        'disable-RX-in-defer':serial.replace('and 0xfd','and 0xfc'),
        'missing-rearm':serial.replace('            or 2\n','            or 0\n'),
        'copy-in-retry':serial.replace('uart0_async_retry:\n','uart0_async_retry:\n otirx\n',1),
        'keep-pending-at-callback':serial.replace('\t\t\txor a\n\t\t\tld (uart0_tx_retry_pending),a\n\t\t\tcall uart0_tx_callback',
                                                '\t\t\tcall uart0_tx_callback'),
        'inactive-retry-reads-port':serial.replace('            ret z\n','            in0 a,(UART0_IER)\n            ret z\n')}
    bad['wrong-defer-frame']=serial.replace('            pop af\n','            pop bc\n',1)
    rejected=[]
    for name,data in bad.items():
        try:source_checks(data,irq,original,old_irq)
        except (AssertionError,IndexError) as e:rejected.append({'name':name,'rejected':True,'reason':str(e)})
        else:raise AssertionError('Negative control accepted: '+name)
    result['negative_controls']=rejected
    spec=importlib.util.spec_from_file_location('startup',donor/'experiments/irq-startup/verify.py')
    startup=importlib.util.module_from_spec(spec);spec.loader.exec_module(startup)
    artifacts={}
    for label in ('original','candidate'):
        root=pair/label;data=(root/'bin/mos.bin').read_bytes()
        symbols=local_symbols(root,'init',tool)
        artifacts[label]={'ROM_bytes':len(data),'SHA256':hashlib.sha256(data).hexdigest(),
                          'CRC32':f'{zlib.crc32(data):08X}','startup':startup.verify(data,symbols),
                          'startup_negative_controls':startup.mutations(data,symbols)}
        assert (root/'src/init.asm').read_bytes()==(pair/'original/src/init.asm').read_bytes(),'Startup source changed'
    root=pair/'candidate';symbols=local_symbols(root,'serial',tool);image=(root/'bin/mos.bin').read_bytes()
    a24=lambda v:v.to_bytes(3,'little')
    flag=symbols['uart0_tx_retry_pending'];fill=symbols['fill_uart0_tx_fifo'];defer=symbols['uart0_tx_defer']
    expected=bytes.fromhex('ed38c1 e6fd ed39c1 3e01 32')+a24(flag)+bytes.fromhex('f1 fb 5bed4d')
    assert image[defer:defer+len(expected)]==expected,'Linked defer bytes differ'
    assert image[fill:fill+7]==bytes.fromhex('ed38a2 ed6408 20'),'Linked CTS entry differs'
    offset=int.from_bytes(image[fill+7:fill+8],'little',signed=True)
    assert fill+8+offset==defer,'Linked blocked branch target wrong'
    retry=symbols['uart0_async_retry']
    expected=bytes.fromhex('3a')+a24(flag)+bytes.fromhex('b7 c8 ed38a2 ed6408 c0 af 32')+a24(flag)+bytes.fromhex('ed38c1 f602 ed39c1 c9')
    assert image[retry:retry+len(expected)]==expected,'Linked bounded-retry bytes differ'
    s=artifacts['candidate']['startup'];assert s['BSS_start']<=flag<s['BSS_start']+s['BSS_bytes']
    vb=map_symbols((root/'bin/mos.map').read_text())['_vblank_handler']
    assert image[vb:vb+64].count(b'\xcd'+a24(retry))==1,'Linked VBlank retry hook missing'
    size_output=subprocess.check_output([str(tool/'bin/ez80-none-elf-size'),*[str(pair/l/'obj'/o) for l in ('original','candidate') for o in ('serial.o','interrupts.o')]],text=True)
    result.update(artifacts=artifacts,linked_contract='PASS',symbols={'retry':retry,'defer':defer,'pending':flag},size_output=size_output,
        ROM_delta=artifacts['candidate']['ROM_bytes']-artifacts['original']['ROM_bytes'],
        BSS_delta=artifacts['candidate']['startup']['BSS_bytes']-artifacts['original']['startup']['BSS_bytes'],
        limits='Structural/source/linked/startup proof only. No ISR/CPU emulator, guest or physical execution.')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True)
    p.add_argument('--toolchain',type=Path,required=True);p.add_argument('--donor',type=Path,required=True)
    a=p.parse_args();result=verify(a.pair,a.toolchain,a.donor)
    (a.pair/'checks/structural.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
