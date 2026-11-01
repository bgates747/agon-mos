"""Compare the built source snapshot and working tree with the proven release."""
import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("build", type=Path)
args = parser.parse_args()
release = "8336409351ee5314e02801a7b72a4f1bb5282519"
protected = (
    "main.c", "src/uart.c", "src/interrupts.asm",
    "src_startup/cstartup.asm", "src_startup/init_params_f92.asm",
)
hashes = {}
with tarfile.open(args.build / "source.tar") as snapshot:
    for name in protected:
        original = subprocess.check_output(
            ["git", "show", release + ":" + name], cwd=root
        )
        assert (root / name).read_bytes() == original, name + ": working source differs"
        assert snapshot.extractfile(name).read() == original, name + ": built source differs"
        hashes[name] = hashlib.sha256(original).hexdigest()
receipt = {"release": "v3.0.2", "commit": release, "unchanged_files": hashes}
(args.build / "protected-release-source.json").write_text(
    json.dumps(receipt, indent=2) + "\n"
)
print("PASS: five protected source files match the working release and build snapshot")
