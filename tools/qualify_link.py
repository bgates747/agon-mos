#!/usr/bin/env python3
"""Exercise final-image guards with corrupt controls and compile shared C/C++ imports."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import check_uart0_native

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--toolchain',type=Path,required=True)
p.add_argument('--elf',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();tool=a.toolchain.resolve()/'bin';elf=a.elf.resolve()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
nm=tool/'ez80-none-elf-nm'
positive=check_uart0_native.check(root,elf,nm)
symbols={parts[2]:int(parts[0],16) for line in subprocess.check_output([str(nm),'-a',str(elf)],text=True).splitlines() if len(parts:=line.split())==3}
original=elf.read_bytes();header=struct.unpack_from('<16sHHIIIIIHHHHHH',original)
def file_offset(address):
    for i in range(header[10]):
        kind,offset,va,pa,size,*rest=struct.unpack_from('<8I',original,header[5]+i*header[9])
        if kind==1 and pa<=address<pa+size:return offset+address-pa
    raise AssertionError('Unmapped test mutation')
core_start=symbols['batch_count'];core_end=symbols['batch_more']
memory=check_uart0_native.elf_image(elf)
core=bytes(memory[i] for i in range(core_start,core_end))
opcode=core_start+core.index(b'\xed\xc3')
controls=[('retired-slot',symbols['mos_function_block_start']+18*3,1,'Retired slot12'),
          ('header-length',symbols['uart0_async_api']+6,53,'Invalid UTX1 header'),
          ('missing-otirx',opcode,0,'Missing/ambiguous native OTIRX')]
results=[]
for name,address,value,message in controls:
    raw=bytearray(original);raw[file_offset(address)]=value
    changed=out/(name+'.elf');changed.write_bytes(raw)
    try:check_uart0_native.check(root,changed,nm)
    except AssertionError as exc:
        assert message in str(exc),(name,str(exc));results.append(dict(name=name,rejected=True,reason=str(exc)))
    else:raise AssertionError('Corrupt control accepted: '+name)
source='''#include <agon/mos.h>
#if MOS_FUNCTION_UART0_ASYNC != 0x13u
#error Wrong canonical UART reservation
#endif
unsigned int uart0_canonical_reservation(void) { return MOS_FUNCTION_UART0_ASYNC; }
'''
imports=[]
for suffix,standard in [('c','gnu17'),('cpp','gnu++17')]:
    src=out/('api-smoke.'+suffix);src.write_text(source)
    obj=src.with_suffix('.o');dep=src.with_suffix('.d')
    subprocess.run([str(tool/'ez80-none-elf-clang'),'-target','ez80-none-elf','-march=ez80',
                    '-std='+standard,'-ffreestanding','-fno-integrated-as','-B'+str(tool),
                    '-mllvm','-z80-gas-style','-Wa,-march=ez80+full',
                    '-I'+str(root/'src/shared-api/api/include'),'-nostdinc',
                    '-isystem',str(a.toolchain.resolve()/'include'),'-MD','-MF',str(dep),
                    '-c',str(src),'-o',str(obj)],check=True)
    text=dep.read_text()
    assert str(root/'src/shared-api/api/include/agon/mos.h') in text
    assert 'mos_api_reservations.h' in text
    assert str(a.toolchain.resolve()/'include/agon/mos.h') in text
    imports.append(dict(language=suffix,passed=True,object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest()))
receipt=dict(passed=True,positive=positive,corrupt_controls=results,canonical_C_CPP_imports=imports)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
