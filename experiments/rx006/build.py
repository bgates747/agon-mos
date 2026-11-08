"""Build only the original RX006 app under an asserted Pi compiler lease."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
import zlib

p = argparse.ArgumentParser(description=__doc__)
for key in ("rom", "map", "sdk", "out"):
    p.add_argument("--" + key, type=Path, required=True)
p.add_argument("--kbvector", type=lambda x: int(x, 0), required=True)
p.add_argument("--tx-admission", choices=("raw", "guarded"), required=True)
p.add_argument("--lease", required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent
sdk = a.sdk.resolve()
out = a.out.resolve()
out.mkdir(parents=True, exist_ok=False)
assert 0xB0000 <= a.kbvector < 0xC0000
kb_addresses = [int(x,16) for x in re.findall(
    r"0x([0-9a-fA-F]+)\s+_user_kbvector\b", a.map.read_text())]
assert kb_addresses == [a.kbvector], ("callback slot/map mismatch",kb_addresses)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(sdk / "lib/libagon.a") == "04e340186590810dd490d01655b50baaca557b7764006598890e845e6fc1252c"
image = a.rom.read_bytes()
assert 0 < len(image) <= 131072
app = out / "fixture"
shutil.copytree(root / "fixture", app)
sources = {str(x.relative_to(app)): sha(x) for x in app.rglob("*") if x.is_file()}
identity = dict(sources=sources, rom_sha256=sha(a.rom), rom_map_sha256=sha(a.map),
                kbvector=a.kbvector, tx_admission=a.tx_admission,
                sdk_library_sha256=sha(sdk / "lib/libagon.a"))
build = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
(app / "src/identity.h").write_text(
    '#define RX_BUILD "' + build + '"\n' +
    f'#define RX_MOS_BYTES {len(image)}u\n#define RX_MOS_CRC 0x{zlib.crc32(image):08X}UL\n' +
    f'#define RX_KBVECTOR 0x{a.kbvector:X}u\n#define RX6_GUARDED_TX {int(a.tx_admission == "guarded")}\n')
py = "/Agon/mystuff/agon-dev-env/.venv/bin/python"
ctl = "/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py"
commands = []


def run(cmd, name):
    subprocess.run([py, ctl, "assert-owner", "--owner", "agon-mos", "--lease", a.lease],
                   check=True, stdout=subprocess.DEVNULL)
    commands.append(dict(command=cmd, cwd=str(app), log=name))
    with (out / name).open("w") as log:
        proc = subprocess.Popen(cmd, cwd=app, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=180)
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=5)
            except ProcessLookupError:
                pass
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            raise
    assert rc == 0, (name, rc)


begin = time.monotonic()
run(["make", "-j1", "AGONDEV_TOOLCHAIN=" + str(sdk)], "compile.log")
objects = [str(x) for x in sorted((app / "obj").glob("*.o"))]
run([str(sdk / "bin/ez80-none-elf-ld"), "-defsym=RAM_START=0x40000",
     "-defsym=RAM_SIZE=0x70000", "-defsym=_has_exit_handler=0",
     "-Map=" + str(out / "test.elf.map"), "-T", str(sdk / "config/linker.conf"),
     "--oformat", "elf32-z80", "-o", str(out / "test.elf"), *objects,
     "-L" + str(sdk / "lib"), "-l", "agon"], "elf-link.log")
run([str(sdk / "bin/ez80-none-elf-objcopy"), "-O", "binary", str(out / "test.elf"),
     str(out / "from-elf.bin")], "elf-copy.log")
assert (out / "from-elf.bin").read_bytes() == (app / "bin/test.noname.bin").read_bytes()
run([str(sdk / "bin/ez80-none-elf-objdump"), "-d", str(out / "test.elf")], "listing.txt")
run([str(sdk / "bin/ez80-none-elf-nm"), "-n", str(out / "test.elf")], "symbols.txt")
symbols = {}
for line in (out / "symbols.txt").read_text().splitlines():
    f = line.split()
    if len(f) == 3:
        try:
            symbols[f[2]] = int(f[0], 16)
        except ValueError:
            pass
for key in ("_bench_witness", "_rx_arm", "_legacy_keyboard", "_tx_submit"):
    assert key in symbols, key
(out / "symbols.json").write_text(json.dumps(symbols, indent=2) + "\n")
assert not any(x in symbols for x in ("_timer_start", "_rx_uart_snapshot", "_tx_temt"))
result = dict(schema="RX006-APP-BUILD1", build=build, identity=identity,
              source_snapshots=sources, fixture_sha256=sha(app / "bin/test.bin"),
              fixture_bytes=(app / "bin/test.bin").stat().st_size,
              witness=symbols["_bench_witness"], commands=commands,
              elapsed_seconds=time.monotonic() - begin,
              qualification="APP LINK ONLY; no firmware installation or target execution")
(out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
