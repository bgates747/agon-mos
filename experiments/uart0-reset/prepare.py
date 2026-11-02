"""Build inputs for the reset appliance, retaining the qualified MOS unchanged."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--attempt',default='fixture');a=p.parse_args()
b=a.build.resolve();b.mkdir(parents=True,exist_ok=True)
original=root/'build/uart0-startup-safe/run004'
for n in ('MOS.bin','MOS.map','symbols.txt'):shutil.copyfile(original/n,b/n)
assert hashlib.sha256((b/'MOS.bin').read_bytes()).hexdigest()=='89ea8694194e0488337bf1dcbfa91e2b084b3afc75a9c3916f4acc9ae12aa42b'
subprocess.run([str(root/'.venv/bin/python'),str(root/'experiments/uart0-startup-safe/prepare_fixture.py'),str(b),'--attempt',a.attempt],check=True)
f=b/a.attempt;(f/'src/main.c').rename(f/'src/baseline.inc')
shutil.copyfile(root/'experiments/uart0-reset/src/main.c',f/'src/main.c')
with (f/'src/uart.src').open('a') as h:h.write('''
.global _reset_call
.global _reset_stop
.extern _reset_arg_hl, _reset_arg_de, _reset_arg_bc
.extern _reset_result_hl, _reset_result_bc
_reset_call:
    push ix
    ld ix,(_safe_function)
    ld hl,(_reset_arg_hl)
    ld de,(_reset_arg_de)
    ld bc,(_reset_arg_bc)
    call reset_api_jump
    ld (_reset_result_hl),hl
    ld (_reset_result_bc),bc
    pop ix
    ret
reset_api_jump:
    jp (ix)
_reset_stop:
    di
reset_stop_forever:
    halt
    jr reset_stop_forever
''')
s={k:int(v,16) for v,_,k in (line.split() for line in (b/'symbols.txt').read_text().splitlines())}
header=f/'src/identity.h';text=header.read_text()
for key,symbol in {'SAFE_BATCH':'tx_cts_batch','SAFE_SYNC_DEPTH':'uart0_sync_depth','SAFE_NEXT_TICKET':'tx_next_ticket','SAFE_GP':'_gp'}.items():text+=f'#define {key} {hex(s[symbol])}\n'
build_id=hashlib.sha256((b/'MOS.bin').read_bytes()+b''.join((f/'src'/n).read_bytes() for n in ('main.c','baseline.inc','uart.src'))).hexdigest()[:16]
data=json.loads((f/'metadata.json').read_text());text=text.replace(data['build_id'],build_id);header.write_text(text)
data.update(build_id=build_id,reset_fixture=True,MOS_unchanged=True,hardware_qualified=False,reset_window_ticks=7200,arm_record_bytes=64)
data['identities']['SAFE_BUILD']='"'+build_id+'"';(f/'metadata.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
