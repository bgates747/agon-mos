"""Check the branded API1.1 MOS and menu using disposable Flexe FAT media."""
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
b = root / 'build/uart0-branding'
engine = sys.argv[1]
assert engine in ('jit', 'interp')
out = b / ('checks-' + engine)
out.mkdir(exist_ok=False)
p = root / '.emulator' / ('uart0-branding-' + engine)
p.mkdir(exist_ok=False)
r = p / 'runtime'
r.mkdir()
h = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
old = root / '.emulator/uart0-race'
files = {
    'flexe-agon-emulator.bin': old / 'flexe-agon-emulator.bin',
    'flexe-vdp.so': old / 'flexe-vdp.so',
    'mos_platform.bin': b / 'branded/MOS.bin',
    'mos_platform.map': b / 'branded/MOS.map',
    'esp32-firmware.bin': root / 'build/uart0-repair/candidate/.pio/build/esp32dev/firmware.bin',
    'esp32-firmware.elf': root / 'build/uart0-repair/candidate/.pio/build/esp32dev/firmware.elf',
}
assert h(files['flexe-agon-emulator.bin']) == '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
assert h(files['flexe-vdp.so']) == '77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'
for name, source in files.items():
    shutil.copyfile(source, r / name)
    if name.endswith('.bin'):
        (r / name).chmod(0o755)
    if name != 'flexe-agon-emulator.bin':
        (p / name).symlink_to('runtime/' + name)
(p / 'fab-agon-emulator.bin').symlink_to('runtime/flexe-agon-emulator.bin')
(p / 'sdcard').mkdir()
image = out / 'card.img'
with image.open('xb') as f:
    f.truncate(32 * 1024 * 1024)
subprocess.run(['mkfs.fat', '-F', '16', str(image)], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['mmd', '-i', str(image), '::/uart0'], check=True)
base = root / 'build/uart0-repair/console8-ab-replay-20261015'
def copyin(source, name):
    subprocess.run(['mcopy', '-i', str(image), str(source), '::/' + name], check=True)
for f in base.glob('*.bin'):
    if not f.name.startswith(('vdp-', 'mos-')) and f.name != 'test.bin':
        copyin(f, 'uart0/' + f.name)
copyin(b / 'test.bin', 'uart0/test.bin')
(out / 'suite.cfg').write_text('board=Branded MOS off-device regression\nvdp_label=RX sync candidate\nvdp_flash=0\nphysical_receiver=0\n')
copyin(out / 'suite.cfg', 'uart0/suite.cfg')
(out / 'autoexec.txt').write_bytes(b'CD /uart0\r\nLOAD test.bin\r\nRUN . 1\r\nLOAD test.bin\r\nRUN . 6\r\nLOAD test.bin\r\nRUN . rx\r\nECHO BRAND RETURN\r\n')
copyin(out / 'autoexec.txt', 'autoexec.txt')
(p / 'sdcard.img').symlink_to(image)
(p / '.mos-release').write_text('Experimental UART0 ABI1.1 banner-only build\n')
(p / '.mos-release.sha256').write_text(''.join(h(p / n) + '  ' + n + '\n' for n in ('mos_platform.bin', 'mos_platform.map')))
(p / '.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
spec = importlib.util.spec_from_file_location('canonical', b / 'canonical_setup.py')
factory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(factory)
factory.write_profile_launcher(p, strict_bespoke=True)
launcher = p / 'fab-agon-emulator'
s = launcher.read_text()
token = 'vdp_name="$(< "${profile_dir}/.bespoke-vdp-profile")"'
assert s.count(token) == 1
s = s.replace(token, '''export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
mkdir -p "$AGON_FLEXE_ARTIFACTS"
''' + token)
token = '        --sdcard "${profile_dir}/sdcard" \\\n'
assert s.count(token) == 2
s = s.replace(token, token + '        --sdcard-img "${profile_dir}/sdcard.img" \\\n')
launcher.write_text(s)
factory.name_flexe_profile(p)
assert not (p / 'fab-agon-emulator').exists() and not (p / 'fab-agon-emulator.bin').exists()
names = [*files, 'flexe-agon-emulator']
(p / '.runtime.sha256').write_text(''.join(h(p / n) + '  ' + n + '\n' for n in names))
subprocess.run(['sha256sum', '--check', '--status', '.runtime.sha256'], cwd=p, check=True)
art = p / 'last-run'
started = time.monotonic()
error = None
proc = None
try:
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', AGON_FLEXE_ENGINE=engine)
    with (out / 'frontend.log').open('w') as log:
        proc = subprocess.Popen(['./flexe-agon-emulator', '--precise-interrupts'], cwd=p, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        while time.monotonic() - started < 180:
            wire = art / 'mos-to-vdp.bin'
            if wire.exists():
                data = wire.read_bytes()
                assert b'Error executing autoexec' not in data, 'Test command failed'
                if b'BRAND RETURN' in data:
                    break
            assert proc.poll() is None, 'Frontend exited early'
            time.sleep(.1)
        else:
            raise TimeoutError('No completion marker')
finally:
    if proc and proc.poll() is None:
        for f in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(f.name)) == proc.pid and (f / 'exe').resolve() == r / 'flexe-agon-emulator.bin':
                    os.kill(int(f.name), signal.SIGTERM)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    if art.exists():
        for f in art.iterdir():
            if f.is_file():
                shutil.copyfile(f, out / f.name)
    (p / 'sdcard.img').unlink()
reports = out / 'reports'
reports.mkdir()
subprocess.run(['mcopy', '-s', '-i', str(image), '::/uart0/*', str(reports)], check=True)
wire = (out / 'mos-to-vdp.bin').read_bytes()
label = b'Arthur - UART0 async EXPERIMENTAL'
assert label in (b / 'branded/MOS.bin').read_bytes()
assert label in wire, 'Experimental banner absent from boot output'
for run, test in ((1, 1), (2, 6), (3, 10)):
    text = (reports / f'R{run:04d}.log').read_text()
    assert 'MOS_ROM128K_CRC32=DD9A1288 API=1.1' in text
    assert f'TEST {test} PASS' in text and f'END run={run:04d} PASS' in text
assert (reports / 'Y0003.dat').read_bytes() == (reports / 'Z0003.dat').read_bytes()
stats = json.loads((out / 'stats.json').read_text())
uart = json.loads((out / 'uart.json').read_text())
assert not any(stats[n] for n in ('failed', 'unhandled', 'unregistered', 'unmapped'))
assert uart['tx_drops'] == uart['rx_overruns'] == 0
receipt = dict(passed=True, engine=engine, elapsed_seconds=round(time.monotonic()-started, 3),
               banner_present=True, API='1.1', ROM128K_CRC32='DD9A1288', physical_erased_ROM_CRC32='44BC5C07',
               menu_sha256=h(b / 'test.bin'), rom_sha256=h(b / 'branded/MOS.bin'),
               test_phases=[1, 6, 10], actual_FatFS=True, hardware_test_performed=False,
               profile=str(p), compiled_ESP32_firmware=True)
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
