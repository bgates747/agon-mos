"""Prepare the standalone original AgonDev experiment and existing ZDS children."""
import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=Path(sys.argv[1]).resolve()
subprocess.run([str(root/'.venv/bin/python'),str(root/'experiments/uart0-startup-safe/prepare_fixture.py'),str(b)],check=True)
f=b/'fixture';(f/'src/main.c').rename(f/'src/baseline.inc');shutil.copyfile(root/'experiments/uart0-completion/src/main.c',f/'src/main.c')
# A persistent seed permits clearing archived report files from physical media.
p=f/'src/baseline.inc';baseline=p.read_text()
old=' for(run_id=1;run_id<10000;run_id++){'
assert old in baseline
baseline=baseline.replace('static int begin(void){','#include "run_counter.inc"\nstatic int begin(void){')
baseline=baseline.replace(old,' unsigned first=first_report();if(!first)return 0;\n for(run_id=first;run_id<10000;run_id++){')
old=' char text[160];snprintf(text,sizeof(text),"UARTSAFE'
assert old in baseline
baseline=baseline.replace(old,' if(!save_next_report(run_id+1)){mos_fclose(log_file);mos_fclose(index_file);return 0;}\n char text[160];snprintf(text,sizeof(text),"UARTSAFE')
p.write_text(baseline)
shutil.copyfile(root/'experiments/uart0-completion/src/run_counter.inc',f/'src/run_counter.inc')

shutil.copyfile(root/'experiments/uart0-completion/library/uart_write.src',f/'src/uart_write.src')
s=(f/'stress/packets.inc').read_text();arrays=''
for n in ('setup','reset_flag','reply','mismatch_probe','match_probe','cleanup'):
 block=re.search(r'^'+n+r':\n(.*?)^'+n+r'_end:',s,re.M|re.S)[1]
 vals=[int(v) for l in block.splitlines() for v in l.strip().removeprefix('DB ').split(',') if v]
 arrays+='static const uint8_t v_'+n+'[]={'+','.join(map(str,vals))+'};\n'
(f/'src/packets.h').write_text(arrays)
with (f/'src/uart.src').open('a') as h:h.write('''
.global _ux_call, _ux_notify
.extern _ux_hl, _ux_de, _ux_bc, _ux_result
.extern _ux_count, _ux_last, _ux_bad, _ux_context
_ux_call:
    push ix
    ld ix,(_safe_function)
    ld hl,(_ux_hl)
    ld de,(_ux_de)
    ld bc,(_ux_bc)
    call ux_jump
    ld (_ux_result),hl
    pop ix
    ret
ux_jump:
    jp (ix)
_ux_notify:
    ld (_ux_context),de
    cp 4
    jr z,ux_status_ok
    ld a,1
    ld (_ux_bad),a
ux_status_ok:
    ld de,(_ux_last)
    ld a,d
    or e
    jr z,ux_first
    inc de
    push hl
    or a
    sbc hl,de
    pop hl
    jr z,ux_first
    ld a,1
    ld (_ux_bad),a
ux_first:
    ld (_ux_last),hl
    ld hl,(_ux_count)
    inc hl
    ld (_ux_count),hl
    ret
''')
hash_input=(b/'MOS.bin').read_bytes()+b''.join((f/'src'/n).read_bytes() for n in ('main.c','baseline.inc','uart.src','packets.h','run_counter.inc'));build=hashlib.sha256(hash_input).hexdigest()[:16]
m=json.loads((f/'metadata.json').read_text());p=f/'src/identity.h';p.write_text(p.read_text().replace(m['build_id'],build));m.update(build_id=build,write_mode_experiment=True,physical_qualification=False);m['identities']['SAFE_BUILD']='"'+build+'"';(f/'metadata.json').write_text(json.dumps(m,indent=2)+'\n')
