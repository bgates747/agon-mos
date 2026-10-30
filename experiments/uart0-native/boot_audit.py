"""Execute actual linked startup/UART instructions on the retained CPU oracle.

Run on Oryx. Register latches and a baud-aware minimal boot peer are modeled;
this is not a physical flash/readback or a silicon timing qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--native', type=Path, required=True)
p.add_argument('--mos-build', required=True)
p.add_argument('--attempt', required=True)
a = p.parse_args()
assert a.attempt.isalnum()
native = a.native.expanduser().resolve(strict=True)
firmware = native / '.build' / a.mos_build / 'bin/MOS.bin'
elf = firmware.with_suffix('.elf')
out = root / 'build/uart0-native' / ('boot-' + a.attempt)
(out / 'src').mkdir(parents=True, exist_ok=False)
source = Path(__file__).with_suffix('.rs')
shutil.copyfile(source, out / 'src/main.rs')
model = root / 'build/uart0-async/ez80-model'
assert (model / 'Cargo.toml').is_file(), 'Restore the archived CPU test dependency'
(out / 'Cargo.toml').write_text('[package]\nname="uart0-boot-audit"\n'
    'version="0.1.0"\nedition="2021"\npublish=false\n[dependencies]\n'
    'ez80={path="../../uart0-async/ez80-model"}\n')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
receipt = dict(passed=False, hardware_qualified=False, ROM_sha256=sha(firmware),
    ELF_sha256=sha(elf), harness_sha256=sha(source),
    CPU_source_sha256={str(f.relative_to(model)): sha(f) for f in sorted(model.rglob('*'))
                      if f.is_file() and '.git' not in f.parts and 'target' not in f.parts},
    scope=['UART0/UART1 divisors at seven rates', 'reset to main, cold/retained RAM',
           'data/BSS/vectors/stack', 'baud-aware boot peer through GP/mode/palette to bootmsg'],
    limits=['flat memory/register latches', 'idealized timer expiry/IRQ delivery',
            'minimal peer, not compiled ESP32 firmware', 'no physical flash readback'])
try:
    with (out / 'build.log').open('w') as log:
        subprocess.run([str(Path.home() / '.cargo/bin/cargo'), 'build', '--offline',
            '--release', '--manifest-path', str(out / 'Cargo.toml')],
            stdout=log, stderr=subprocess.STDOUT, check=True)
    with (out / 'symbols.txt').open('w') as log:
        subprocess.run([str(native.parent / 'toolchain/bin/ez80-none-elf-nm'),
            '-an', str(elf)], stdout=log, check=True)
    run = subprocess.run([str(out / 'target/release/uart0-boot-audit'), str(firmware),
        str(out / 'symbols.txt')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (out / 'execution.log').write_text(run.stdout)
    receipt.update(passed=run.returncode == 0, returncode=run.returncode)
    print(run.stdout)
except Exception as exc:
    receipt['error'] = repr(exc)
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k:v for k,v in receipt.items() if k != 'CPU_source_sha256'}, indent=2))
sys.exit(0 if receipt['passed'] else 1)
