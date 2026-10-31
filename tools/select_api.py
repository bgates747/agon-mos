#!/usr/bin/env python3
"""Export or verify the exact canonical API package; never generate private IDs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'dependencies.json').read_text())
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--foundation',type=Path,help='Local canonical repository; read the pinned commit, never its dirty files')
a=p.parse_args()
out=root/'src/shared-api'
if a.foundation:
    expected=lock['foundation']['commit']
    subprocess.run(['git','-C',str(a.foundation),'cat-file','-e',expected+'^{commit}'],check=True)
    payload={}
    for name,pin in lock['api_files'].items():
        data=subprocess.check_output(['git','-C',str(a.foundation),'show',expected+':'+name])
        assert hashlib.sha256(data).hexdigest()==pin,name
        payload[name]=data
    for name,data in payload.items():
        target=out/name
        assert not target.is_symlink()
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==data,'Changed shared API dependency: '+name
        else:target.write_bytes(data)
for name,pin in lock['api_files'].items():
    target=out/name
    assert target.is_file() and not target.is_symlink(), 'Run select_api.py --foundation PATH first: '+name
    assert hashlib.sha256(target.read_bytes()).hexdigest()==pin,name
print('Pinned canonical API package verified; no private definitions or owner changes.')
