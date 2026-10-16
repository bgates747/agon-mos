"""Use the canonical generator for the project-owned, stopped Oryx profile."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[2]
build = root / "build/uart0-mos"
profile = root / ".emulator"
spec = importlib.util.spec_from_file_location("canonical_profiles", build / "setup_emulator.py")
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)
reference = root.parent / "golem/.emulator/runtime/fab-1.2.5"
product = build / "runtime"
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
app = profile / "sdcard/uart"
app.mkdir(exist_ok=True)
shutil.copyfile(build / "app.bin", app / "app.bin")
shutil.copyfile(build / "short.bin", app / "short.bin")
(profile / "sdcard/autoexec.txt").write_bytes(b"SET KEYBOARD 1\r\ncd /uart\r\nload app.bin\r\nrun\r\nECHO UART0 RETURN ONE PASS\r\nload app.bin\r\nrun\r\nECHO UART0 RETURN TWO PASS\r\nload short.bin\r\nrun\r\nECHO UART0 MOS INTEGRATION PASS\r\nUART0_BAD_COMMAND\r\n")
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
rm -f -- "$profile_dir/sdcard/uart/integrated.dat" "$profile_dir/sdcard/uart/failure.dat"

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
identity = [*files, "flexe-agon-emulator", "sdcard/uart/app.bin", "sdcard/uart/short.bin", "sdcard/autoexec.txt"]
(profile / ".runtime.sha256").write_text("".join(
    f"{hashlib.sha256((profile/name).read_bytes()).hexdigest()}  {name}\n" for name in identity))
print(f"Prepared stopped profile: {profile}")
