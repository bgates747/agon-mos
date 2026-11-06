# SPDX-License-Identifier: MIT
"""Check linked post-syscall carry conversion, not UART or target execution.

Supply a MOS successful/failed carry result to the actual linked wrapper's tiny
return path. The retained failing SDK wrapper is the negative control. Unknown
instructions fail closed; this is deliberately not an eZ80/UART emulator.
"""
from pathlib import Path
import json,re,sys

binary,mapfile,symbol,expected=sys.argv[1:]
match=re.search(r'^\s*0x([0-9a-fA-F]+)\s+'+re.escape(symbol)+r'\s*$',Path(mapfile).read_text(),re.M)
assert match,'missing linked symbol '+symbol
address=int(match[1],16)
code=Path(binary).read_bytes()[address-0x40000:address-0x40000+48]
entry=code.index(b'\x5b\xcf')+2 # RST.LIL 08h

def returned(carry):
    pc=entry;a=None
    for _ in range(12):
        op=code[pc];pc+=1
        if op==0x3e:a=code[pc];pc+=1 # LD A,n leaves flags intact
        elif op in (0x30,0x38):
            delta=code[pc];pc+=1
            if delta>=128:delta-=256
            if bool(carry)==(op==0x38):pc+=delta
        elif op==0xaf:a=0;carry=0 # XOR A
        elif op==0xc9 or (op==0xd8 and carry):return a
        elif op!=0xd8:raise AssertionError('unexpected post-syscall instruction '+hex(op))
    raise AssertionError('return path did not terminate')

actual={'success':returned(1),'failure':returned(0)}
wanted={'success':1,'failure':0} if expected=='correct' else {'success':0,'failure':1}
assert expected in ('correct','inverted') and actual==wanted,(actual,wanted)
print(json.dumps({'symbol':symbol,'linked_address':hex(address),'mos_carry_conversion':actual,
                  'classification':expected,'guest_executed':False}))
