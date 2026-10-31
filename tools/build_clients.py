#!/usr/bin/env python3
"""Build native public-API stress clients with the pinned packet corpus."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--toolchain',type=Path,required=True)
p.add_argument('--packets',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
assert hashlib.sha256(a.packets.read_bytes()).hexdigest()=='1c632115f137f776e95e402227b36769c224b627a4e6d62e26d52fb22fa35570'
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
shutil.copyfile(a.packets,out/'packets.inc')
tool=a.toolchain.resolve()/'bin'
receipts=[]
for n,negative in [(1,True)]+[(n,False) for n in (1,2,4,8,16)]:
    stem='stress1-no-quiescence' if negative else f'stress{n}'
    command=[str(tool/'ez80-none-elf-as'),'-march=ez80+full+adl','-I','src',
             '-I',str(out),'--defsym',f'UART_TEST_CTS_BATCH={n}',
             '--defsym',f'UART_TEST_NO_QUIESCENCE={int(negative)}',
             'tests/clients/stress.asm','-o',str(out/(stem+'.o'))]
    subprocess.run(command,cwd=root,check=True)
    subprocess.run([str(tool/'ez80-none-elf-ld'),'-T','tests/clients/client.ld',
                    '-Map',str(out/(stem+'.map')),'-o',str(out/(stem+'.elf')),
                    str(out/(stem+'.o'))],cwd=root,check=True)
    subprocess.run([str(tool/'ez80-none-elf-objcopy'),'-O','binary',
                    str(out/(stem+'.elf')),str(out/(stem+'.bin'))],check=True)
    raw=(out/(stem+'.bin')).read_bytes()
    assert raw[64:69]==b'MOS\x00\x01'
    receipts.append(dict(name=stem,batch=n,negative_control=negative,bytes=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest()))
(out/'clients.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(receipts,indent=2))
