"""Prepare a new stopped profile from the verified FX-291 runtime."""
from hashlib import sha256
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

incoming = Path(__file__).resolve().parent
profile = Path(sys.argv[1])
freeze = json.loads((incoming / "profile-pins.json").read_text())
donor = Path(freeze["profile"])

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

launch_names = (
    "flexe-agon-emulator", "flexe-agon-emulator.bin", "flexe-vdp.so",
    ".bespoke-vdp-profile", "esp32-firmware.bin", "esp32-firmware.elf",
)
for name in launch_names:
    assert digest(donor / name) == freeze["hashes"][name], name

profile.mkdir(parents=True, exist_ok=False)
(profile / "sdcard").mkdir()
(profile / "runtime").mkdir()
for name in launch_names:
    if name == "flexe-agon-emulator.bin":
        shutil.copy2(donor / name, profile / "runtime/emulator")
        (profile / name).symlink_to("runtime/emulator")
    else:
        shutil.copy2(donor / name, profile / name)
for name in ("bin", "map"):
    shutil.copy2(incoming / f"mos.{name}", profile / f"mos_platform.{name}")
subprocess.run(["sha256sum", "-c", str(incoming / "candidate.sha256")],
               cwd=profile, check=True)
launcher = profile / "flexe-agon-emulator"
body = launcher.read_text()
assert body.count("unset LD_PRELOAD\n") == 1
launcher.write_text(body.replace("unset LD_PRELOAD\n", ""))
(profile / ".mos-release").write_text("RC3 NMI-001 proof R01\n")
mos = ["mos_platform.bin", "mos_platform.map"]

def pins(name, paths):
    (profile / name).write_text("".join(f"{digest(profile / x)}  {x}\n" for x in paths))

pins(".mos-release.sha256", mos)
helper = runpy.run_path(str(incoming / "flexe_profile.py"))
helper["name_flexe_profile"](profile)
helper["verify_profile_executables"](launcher, profile / "flexe-agon-emulator.bin")
pins(".runtime.sha256", [*launch_names, *mos, ".mos-release", ".mos-release.sha256",
      "/usr/lib/x86_64-linux-gnu/libSDL3.so.0"])
shutil.copyfile(incoming / "run_oryx.py", profile / "run_oryx.py")
subprocess.run(["bash", "-n", str(launcher)], check=True)
assert not list((profile / "sdcard").iterdir())
