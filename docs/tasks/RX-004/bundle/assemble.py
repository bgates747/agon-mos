"""Package a prepared, audited reproduction tree; verify a clean extraction."""
from pathlib import Path
import argparse,hashlib,json,tempfile,zipfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('tree',type=Path);p.add_argument('output',type=Path)
a=p.parse_args();root=a.tree.resolve();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
files={str(f.relative_to(root)):dict(bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(root.rglob('*')) if f.is_file() and str(f.relative_to(root)) not in ('SHA256SUMS','manifest.json')}
(root/'manifest.json').write_text(json.dumps(dict(format_version=1,files=files),indent=2)+'\n')
files['manifest.json']=dict(bytes=(root/'manifest.json').stat().st_size,sha256=sha(root/'manifest.json'))
(root/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+n+'\n' for n,v in sorted(files.items())))
with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file():
   info=zipfile.ZipInfo(str(f.relative_to(root)),date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with tempfile.TemporaryDirectory(prefix='rx004-zip-', dir=a.output.resolve().parent) as d:
 with zipfile.ZipFile(a.output) as z:
  assert z.testzip() is None
  z.extractall(d)
 extracted=Path(d)
 for n,v in files.items():
  f=extracted/n;assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256'],n
 # Check the decoder directly from the unpacked download.
 import subprocess,sys
 subprocess.run([sys.executable,str(extracted/'tools/check_pair.py'),str(extracted/'evidence/hardware/U0012.dat'),str(extracted/'evidence/hardware/U0014.dat')],check=True,stdout=subprocess.DEVNULL)
result=dict(zip=str(a.output),bytes=a.output.stat().st_size,sha256=sha(a.output),files=len(files)+1,clean_extraction_hashes_verified=True,unpacked_pair_decoder_passed=True)
a.output.with_suffix('.verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
