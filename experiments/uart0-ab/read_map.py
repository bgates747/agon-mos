"""Read native ZDS output; no assembly translation."""
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);text=(p/'driver.map').read_text()
segments=re.findall(r'^\s*(UART_DRIVER|UART_FIXTURE)\s+normal data\s+C:([0-9A-F]+)\s+C:([0-9A-F]+)\s+([0-9A-F]+)h\s*$',text,re.I|re.M)
assert len(segments)==2
segments.sort(key=lambda x:int(x[1],16));a,b=segments
assert a[0]=='UART_DRIVER' and b[0]=='UART_FIXTURE' and int(a[1],16)==0x40000 and int(a[2],16)+1==int(b[1],16)
syms=re.findall(r'^(\w+)\s+C:([0-9A-F]+)\s+(?:driver|fixture)\s+(?:UART_DRIVER|UART_FIXTURE)\s*$',text,re.I|re.M)
assert syms and len({n for n,v in syms})==len(syms)
(p/'symbols.txt').write_text(''.join(f'{v} T {n}\n' for n,v in syms))
size=int(b[2],16)-0x40000+1;image=(p/'driver.bin').read_bytes();assert len(image)<=size
(p/'driver.bin').write_bytes(image.ljust(size,b'\0'))
