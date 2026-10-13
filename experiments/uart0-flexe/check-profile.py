"""Prove a missing explicit backend fails closed before an emulator boots."""
from pathlib import Path
import os
import subprocess

root=Path(__file__).resolve().parents[2]
profile=root/".emulator"
module=profile/"flexe-vdp.so"
missing=profile/"flexe-vdp.so.absent"
assert module.is_symlink() and not missing.exists()
module.rename(missing)
try:
    run=subprocess.run(["./flexe-agon-emulator"],cwd=profile,
        env=dict(os.environ,SDL_VIDEODRIVER="dummy",SDL_AUDIODRIVER="dummy"),
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=10)
    assert run.returncode != 0 and b"runtime identity mismatch" in run.stdout, run.stdout
    assert b"Loaded ESP32 image" not in run.stdout, run.stdout
finally:
    missing.rename(module)
subprocess.run(["sha256sum","--check","--status",".runtime.sha256"],cwd=profile,check=True)
print("PASS missing Flexe adapter rejected before boot; pinned profile restored")
