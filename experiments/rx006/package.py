"""Repackage the unchanged fixture with Eirene numeric syntax; no device/build."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--previous', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--directory', required=True)
a = p.parse_args()
assert a.directory.startswith('/test/mos-rx006-')
assert all(c.isalnum() or c in '/-' for c in a.directory)
old = json.loads(a.previous.read_text())
assert old['schema'] == 'RX006-KIT1' and a.directory != old['sd_directory']
for name, pin in old['files'].items():
    data = Path(pin['path']).read_bytes()
    assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256']
out = a.out.resolve()
out.mkdir(parents=True, exist_ok=False)
package = out / 'package'
package.mkdir()
suite = (f"CD {a.directory}\r\ntest\r\n"
         f"SAVE {a.directory}/WITNESS.BIN &{old['witness_address']:X} &{old['witness_bytes']:X}\r\n"
         "CD /\r\nEMOS sdserve --fast /\r\n").encode('ascii')
kit = dict(old, sd_directory=a.directory, files={},
           previous_kit_sha256=hashlib.sha256(a.previous.read_bytes()).hexdigest(),
           qualification='Unchanged app/firmware; corrected explicit hex SAVE batch; completion confirmation pending')
for name, pin in old['files'].items():
    data = suite if name == 'suite.txt' else Path(pin['path']).read_bytes()
    if name == 'readme.txt':
        data = data.replace(old['sd_directory'].encode(), a.directory.encode())
    target = package / name
    target.write_bytes(data)
    kit['files'][name] = dict(path=str(target), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
assert kit['files']['test.bin']['sha256'] == old['fixture_sha256']
(out / 'kit.json').write_text(json.dumps(kit, indent=2) + '\n')
print(json.dumps(dict(kit=str(out / 'kit.json'), sha256=hashlib.sha256((out / 'kit.json').read_bytes()).hexdigest(),
                      suite=suite.decode('ascii'), no_device_or_build=True), indent=2))
