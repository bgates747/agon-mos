"""Prepare original menu and native ZDS test children in a fresh build tree."""
import argparse,hashlib,json,re,shutil,subprocess,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--attempt',default='fixture');a=p.parse_args()
assert a.attempt.isalnum()
b=a.build.resolve();f=b/a.attempt;f.mkdir(exist_ok=False)
(f/'src').mkdir();shutil.copyfile(root/'experiments/uart0-startup-safe/Makefile',f/'Makefile')
shutil.copyfile(root/'experiments/uart0-startup-safe/src/main.c',f/'src/main.c')
s=(root/'experiments/uart0-suite/src/uart.src').read_text()+'''
.global _safe_call
.extern _safe_function
_safe_call:
    ld hl,(_safe_function)
    jp (hl)
'''
(f/'src/uart.src').write_text(s)
subprocess.run(['ruby',str(root/'experiments/uart0-stress/packets.rb'),str(f/'stress')],check=True)
stress=f/'stress';info=json.loads((stress/'expected.json').read_text());inc=(stress/'packets.inc').read_text()
for n,pause in enumerate((0,1,4,8)):
 original=(stress/f'packet{n}.bin').read_bytes();prefix=6+3*pause
 ack=original[:prefix]
 for off in range(prefix,len(original),268):
  piece=original[off:off+268];assert len(piece)==268;ack+=piece[-4:]+piece[:-4]
 (stress/f'packet{n}.bin').write_bytes(ack)
 replacement=f'packet{n}:\n'+''.join('    DB '+','.join(map(str,ack[i:i+24]))+'\n' for i in range(0,len(ack),24))+f'packet{n}_end:\n'
 inc,count=re.subn(rf'packet{n}:.*?packet{n}_end:\n',replacement,inc,flags=re.S);assert count==1
 info['packet_sha256'][n]=hashlib.sha256(ack).hexdigest()
(stress/'packets.inc').write_text(inc);(stress/'expected.json').write_text(json.dumps(info,indent=2)+'\n')
shutil.copyfile(root/'experiments/uart0-startup-safe/src/stress.asm',stress/'stress.asm')
(stress/'stress.linkcmd').write_text((root/'experiments/uart0-stress/stress.linkcmd').read_text().replace('$040000 : $04FFFF','$080000 : $08FFFF'))
shutil.copyfile(stress/'checks.bin',f/'checks.bin')
app=f/'app';app.mkdir();subprocess.run(['ruby',str(root/'experiments/uart0-flexe/packets.rb'),str(app)],check=True)
s=(root/'experiments/uart0-mos/app.asm').read_text();controls='    DB "UTC1"\n'
for name,default in [('result_name','integrated.dat'),('baseline_name','api-base.dat'),('failure_name','failure.dat')]:
 match=re.search(r'^'+name+r': DB "([^"]+)",0\n',s,re.M)
 line=match[0] if match else f'{name}: DB "{default}",0\n';text=match[1] if match else default
 controls+=line+f'    DS {16-len(text)-1}\n';s=s.replace(line,'')
s=s.replace('    DB "MOS",0,1\n','    DB "MOS",0,1\n'+controls)
s=s.replace('    ld (diagnostics),hl','    ld (diagnostics),hl\n    ld a,1\n    ld (api_installed),a')
s=s.replace('saved_sp:','api_installed: DB 0\nopen_tries: DB 0,0,0\nsaved_sp:')
old='    call tx_open\n    or a,a\n    jp nz,failed'
retry='''    ld hl,100000
    ld (open_tries),hl
open_try:
    call tx_open
    cp a,1
    jr nz,open_done
    ld hl,(open_tries)
    dec hl
    ld (open_tries),hl
    ld a,h
    or a,l
    jp z,failed
    jr open_try
open_done:
    or a,a
    jp nz,failed'''
assert old in s;s=s.replace(old,retry,1)
s=s.replace('failed:\n    ei','''failed:
    ld a,(api_installed)
    or a,a
    jr z,save_failure
failed_drain:
    call tx_poll_drain
    cp a,1
    jr z,failed_drain
    call tx_close
save_failure:
    ei''')
s=s.replace('    halt\n    jr failed_hold','''    ld sp,(saved_sp)
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ld hl,1
    ret''')
(app/'app.asm').write_text(s);(app/'app.linkcmd').write_text((root/'experiments/uart0-mos/app.linkcmd').read_text().replace('$040000 : $04FFFF','$080000 : $08FFFF'))
for n in ('entry.asm','entry.linkcmd'):shutil.copyfile(root/'experiments/uart0-suite'/n,f/n)
rom=(b/'MOS.bin').read_bytes();syms={k:int(v,16) for v,_,k in (line.split() for line in (b/'symbols.txt').read_text().splitlines())}
assert len(rom)<131072
h=hashlib.sha256(rom+(f/'src/main.c').read_bytes()+(f/'src/uart.src').read_bytes()).hexdigest()[:16]
values={'SAFE_BUILD':'"'+h+'"','SAFE_ROM_CRC':f'0x{zlib.crc32(rom+bytes([255])*(131072-len(rom))):08X}UL','SAFE_FLEXE_CRC':f'0x{zlib.crc32(rom+bytes(131072-len(rom))):08X}UL','SAFE_OPENED':hex(syms['tx_opened']),'SAFE_INITIALIZED':hex(syms['uart0_initialized']),'SAFE_VECTOR':hex(syms['__2nd_jump_table']+0x31),'SAFE_STOCK_ISR':hex(syms['_uart0_handler']),'SAFE_ASYNC_ISR':hex(syms['tx_isr'])}
(f/'src/identity.h').write_text(''.join(f'#define {k} {v}\n' for k,v in values.items())+'static const unsigned SAFE_STRESS_BYTES[]={'+','.join(map(str,info['packet_bytes']))+'};\n')
(f/'metadata.json').write_text(json.dumps(dict(build_id=h,MOS_sha256=hashlib.sha256(rom).hexdigest(),identities=values,stress=info,firmware_compiler='ZDS II',menu_compiler='AgonDev',hardware_qualified=False),indent=2)+'\n')
print('Prepared fixture',f)
