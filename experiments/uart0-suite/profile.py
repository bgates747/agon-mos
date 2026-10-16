"""Use the canonical generator for the project-owned, stopped Oryx profile."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[2]
build = root / "build/uart0-suite"
assert sys.argv[1:] in ([], ["--auto"], ["--keys"])
suffix = "-auto" if sys.argv[1:] == ["--auto"] else "-keys" if sys.argv[1:] else ""
profile = root / (".emulator/uart0-suite" + suffix)
# Never truncate a mapped runtime or replace a human's live profile.
for entry in Path('/proc').glob('[0-9]*'):
    try:
        if (entry/'exe').resolve() == (profile/'runtime/flexe-agon-emulator.bin').resolve():
            raise RuntimeError(f'Close the active UART suite emulator first (PID {entry.name})')
    except (FileNotFoundError, PermissionError):
        pass
spec = importlib.util.spec_from_file_location("canonical_profiles", build / "setup_emulator.py")
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)
reference = root.parent / "golem/.emulator/runtime/fab-1.2.5"
product = root / "build/uart0-mos/runtime"
canonical.link_shared_runtime(profile, reference)
# Copy mutable external artifacts once into our own runtime, then pin them.
runtime = profile / "runtime"
runtime.mkdir(exist_ok=True)
files = {
    "flexe-agon-emulator.bin": product / "flexe-agon-emulator",
    "flexe-vdp.so": product / "flexe-vdp.so",
    "esp32-firmware.bin": product / "esp32-firmware.bin",
    "esp32-firmware.elf": product / "esp32-firmware.elf",
    "mos_platform.bin": build / "MOS.bin",
    "mos_platform.map": build / "MOS.map",
}
for name, source in files.items():
    shutil.copy2(source, runtime / name)
    canonical.replace_symlink(profile / name, runtime / name)
firmware = profile / "firmware"
assert firmware.is_symlink()
firmware.unlink()
app = profile / "sdcard/uart0"
app.mkdir(exist_ok=True)
shutil.copyfile(build / "test.bin", app / "test.bin")
shutil.copyfile(build / "checks.bin", app / "checks.bin")
shutil.copyfile(build / "margin.bin", app / "margin.bin")
for kind in ("bench", "stress"):
    shutil.copyfile(build / kind / f"{kind}.bin", app / f"{kind}.bin")
for kind in ("app", "short"):
    shutil.copyfile(build / "api" / f"{kind}.bin", app / f"{kind}.bin")
for name in ("flash.bin", "mos-candidate.bin", "vdp-2.16.0.bin", "suite.cfg"):
    shutil.copyfile(build / name, app / name)
# The app-only frozen VDP has no qualified OTA update path. The disposable
# key harness alone enables dispatch to prove both upstream N-cancel paths.
cfg=(app/'suite.cfg').read_text()
label='Oryx Flexe human review' if not suffix else 'Oryx Flexe headless qualification'
cfg='\n'.join('board='+label if line.startswith('board=') else
    'vdp_label=Golem VDP snapshot 2.16.0; stock command APIs' if line.startswith('vdp_label=') else
    'vdp_flash='+('1' if suffix=='-keys' else '0') if line.startswith('vdp_flash=') else line
    for line in cfg.splitlines())+'\n'
(app/'suite.cfg').write_text(cfg)
cfg=cfg.replace('physical_receiver=1','physical_receiver=0')
(app/'suite.cfg').write_text(cfg)
# Human review has the same on-card instructions as the physical package.
if not suffix:
    for name in ('readme.txt','firmware.txt'):
        shutil.copyfile(root/'experiments/uart0-suite'/name,app/name)
    shutil.copyfile(root/'experiments/uart0-stress/capture.txt',app/'capture.txt')
    shutil.copyfile(root/'experiments/uart0-bench/analyze.rb',app/'capture-analyze.rb')
commands = b"run . auto\r\nrun . auto\r\nrun . 1\r\nECHO UART0 SUITE AUTO RETURN PASS\r\n" if suffix == "-auto" else b"run\r\nECHO UART0 SUITE RETURN TO MOS\r\n"
(profile / "sdcard/autoexec.txt").write_bytes(b"cd /uart0\r\nload test.bin\r\n"+commands)
(profile / ".bespoke-vdp-profile").write_text("flexe-vdp.so\n")
canonical.write_profile_launcher(profile, strict_bespoke=True)
launcher = profile / "fab-agon-emulator"
text = launcher.read_text().replace("fab-agon-emulator.bin", "flexe-agon-emulator.bin").replace("FSIM", "Flexe Agon Emulator")
assert text.count("\nvdp_name=") == 1
text = text.replace("\nvdp_name=", '''
export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
mkdir -p "$AGON_FLEXE_ARTIFACTS"
# Versioned results are retained; the test harness clears only its disposable profile.

vdp_name=''', 1)
primary = profile / "flexe-agon-emulator"
primary.write_text(text)
primary.chmod(0o755)
launcher.unlink()
(profile / "fab-agon-emulator.bin").unlink()
# This dedicated development profile intentionally boots the candidate ROM.
(profile / ".mos-release").write_text("ASY-001 development MOS; native ZDS II\n")
(profile / ".mos-release.sha256").write_text("".join(
    f"{hashlib.sha256((profile/name).read_bytes()).hexdigest()}  {name}\n"
    for name in ("mos_platform.bin", "mos_platform.map")))
identity = [*files, "sdcard/uart0/margin.bin", "sdcard/uart0/mos-candidate.bin", "sdcard/uart0/vdp-2.16.0.bin", "flexe-agon-emulator", "sdcard/uart0/test.bin", "sdcard/uart0/checks.bin", "sdcard/uart0/bench.bin", "sdcard/uart0/stress.bin", "sdcard/uart0/app.bin", "sdcard/uart0/short.bin", "sdcard/uart0/flash.bin", "sdcard/uart0/suite.cfg", "sdcard/autoexec.txt"]
if not suffix:
    identity += ['sdcard/uart0/readme.txt','sdcard/uart0/firmware.txt','sdcard/uart0/capture.txt','sdcard/uart0/capture-analyze.rb']
(profile / ".runtime.sha256").write_text("".join(
    f"{hashlib.sha256((profile/name).read_bytes()).hexdigest()}  {name}\n" for name in identity))
print(f"Prepared stopped profile: {profile}")
