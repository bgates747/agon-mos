"""Generate the unchanged payload and the versioned ZDS regression fixture."""
import hashlib,json,shutil,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-repair/native';b.mkdir(parents=True,exist_ok=True)
payload=bytes(((n*157+7)%254)+1 for n in range(4096))
s='cases: DB 0,0,1,0\nlabels:\n'
for i,text in enumerate(('Case 1/2: ordinary full-buffer recovery...',
                         'Case 2/2: competing-core recovery during the bounded pause...')):
    assert len(text)<=61
    s+=f'label{i}: DB "{text}",13,10,0\n'
    if len(text)<61:s+=f'    DS {61-len(text)}\n'
s+='payload:\n'+''.join('    DB '+','.join(map(str,payload[i:i+24]))+'\n' for i in range(0,len(payload),24))+'    DB 0\npayload_end:\n'
(b/'cases.inc').write_text(s)
shutil.copyfile(root/'experiments/uart0-repair/host.asm',b/'host.asm')
shutil.copyfile(root/'experiments/uart0-margin/host.linkcmd',b/'host.linkcmd')
(b/'expected.json').write_text(json.dumps(dict(report_bytes=332,record_bytes=160,payload_bytes=4096,payload_crc32=f'{zlib.crc32(payload):08X}',source_sha256=hashlib.sha256((b/'host.asm').read_bytes()).hexdigest(),name_offsets=[73,89,105,121],expected_variant_offset=137),indent=2)+'\n')
