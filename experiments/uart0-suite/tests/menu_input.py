"""Real SDL keyboard regression against the unchanged, compiled diagnostic VDP.

Run on Oryx. The disposable profile never flashes hardware or touches the SD.
Optional old image establishes which tap timings the old MOS getch loses.
"""
import argparse, hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--image', type=Path, required=True)
parser.add_argument('--engine', choices=('jit', 'interp'), default='jit')
parser.add_argument('--label', required=True)
parser.add_argument('--probe', action='store_true')
parser.add_argument('--packets', action='store_true')
args = parser.parse_args()
image = args.image.resolve(strict=True)
b = root / 'build/uart0-ui'
source = root / '.emulator/uart0-race'
p = root / '.emulator/uart0-ui'
dest = b / args.label
dest.mkdir(exist_ok=False)
for proc in Path('/proc').glob('[0-9]*'):
    try:
        assert (proc / 'exe').resolve() != p / 'runtime/flexe-agon-emulator.bin', 'UI profile active'
    except (FileNotFoundError, PermissionError):
        pass
if not p.exists():
    shutil.copytree(source, p, symlinks=True, ignore=shutil.ignore_patterns('sdcard', 'last-run'))
app = p / 'sdcard/uart0'
if app.exists():
    shutil.rmtree(app)
app.mkdir(parents=True)
base = root / 'build/uart0-race/hardware-return-001'
for f in base.iterdir():
    if f.name.endswith(('.bin', '.dat', '.log')) or f.name == 'suite.cfg':
        shutil.copyfile(f, app / f.name)
shutil.copyfile(image, app / 'test.bin')
(app / 'suite.cfg').write_text('board=Oryx menu input regression\nvdp_label=compiled recovery diagnostic\nvdp_flash=0\nphysical_receiver=0\n')
preserved = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in app.iterdir()
             if f.suffix in ('.dat', '.log') and f.name != 'runs.log'}
prior_index = (app/'runs.log').read_bytes()
(p / 'sdcard/autoexec.txt').write_bytes(b'cd /uart0\r\nload test.bin\r\nrun\r\nECHO UI RETURN\r\n')
names = ['flexe-agon-emulator.bin', 'flexe-vdp.so', 'mos_platform.bin', 'mos_platform.map',
         'esp32-firmware.bin', 'esp32-firmware.elf', 'fab-agon-emulator', 'flexe-agon-emulator',
         'sdcard/autoexec.txt', 'sdcard/uart0/test.bin', 'sdcard/uart0/race.bin']
(p / '.runtime.sha256').write_text(''.join(f'{hashlib.sha256((p/n).read_bytes()).hexdigest()}  {n}\n' for n in names))
art = p / 'last-run'
art.mkdir(exist_ok=True)
for f in art.iterdir():
    if f.is_file():
        f.unlink()
keys = dest / 'keys'
keys.write_bytes(b'')
cursor = 0
process = None
started = time.monotonic()
checks = []
failure = None

def wire():
    f = art / 'mos-to-vdp.bin'
    return f.read_bytes() if f.exists() else b''

def wait(marker, timeout=20):
    global cursor
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        data = wire()
        at = data.find(marker, cursor)
        if at >= 0:
            cursor = at + len(marker)
            return
        if process.poll() is not None:
            raise RuntimeError('Emulator exited')
        time.sleep(.03)
    raise TimeoutError(f'{marker!r}; last output: {wire()[-180:]!r}')

def key(value):
    with keys.open('ab') as f:
        f.write(value)

try:
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               AGON_FLEXE_ENGINE=args.engine, LD_PRELOAD=str(b/'keys.so'), UART_SUITE_KEYS=str(keys))
    with (dest/'frontend.log').open('w') as log:
        process = subprocess.Popen(['./fab-agon-emulator', '--precise-interrupts'], cwd=p,
                                   env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        if args.packets:
            wait(b'MENU PACKET QUEUE PASS:')
            wait(b'UI RETURN')
            checks.append('physical_packet_paths_on_eZ80')
            raise StopIteration
        wait(b'Press a choice key:')
        key(b'%9')
        wait(b'VDP flashing is unavailable in this emulator profile.')
        # Tap after the full submenu has been idle, not while it prints.
        time.sleep(1)
        key(b'~0')
        wait(b'Press a choice key:', 4)
        checks.append('late_zero_hold_SDL_tap')
        if not args.probe:
            for i in range(8):
                key(b'#9')
                wait(b'VDP flashing is unavailable in this emulator profile.')
                time.sleep(.1)
                key(b'#0')
                wait(b'Press a choice key:')
            checks.append('eight_submenu_short_taps')
            key(b'^8')
            wait(b'Q Back\r\nChoose:')
            time.sleep(.7)
            key(b'#q')
            wait(b'Press a choice key:')
            checks.append('held_key_one_selection_and_experiment_back')
            key(b'#9')
            wait(b'VDP flashing is unavailable in this emulator profile.')
            key(b'#\nx')
            time.sleep(.3)
            assert b'Press a choice key:' not in wire()[cursor:]
            key(b'#2')
            wait(b'Run 0010: SKIP')
            wait(b'Press a choice key:')
            checks.append('ignore_invalid_keys_and_safe_firmware_selection_with_existing_journal')
            key(b'%8')
            wait(b'Q Back\r\nChoose:')
            key(b'%4')
            wait(b'Run 0011: PENDING', 90)
            wait(b'Press any key for menu.')
            key(b'# ')
            wait(b'Press a choice key:')
            checks.append('callback_detached_for_native_async_session_and_reattached_after')
            assert 'TEST 12 PENDING' in (app/'R0011.log').read_text()
            assert (app/'U0011.dat').read_bytes() == (app/'O0011.dat').read_bytes()
            assert 'FLASH_HANDOFF' not in (app/'R0010.log').read_text()
            assert not (app/'V0011.dat').exists()
        key(b'%q')
        wait(b'UART0 SUITE RETURN PASS')
        wait(b'UI RETURN')
        checks.append('returned_to_MOS')
except StopIteration:
    pass
except Exception as error:
    failure = str(error)
finally:
    if process and process.poll() is None:
        for proc in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(proc.name)) == process.pid and (proc/'exe').resolve() == (p/'runtime/flexe-agon-emulator.bin').resolve():
                    os.kill(int(proc.name), signal.SIGTERM)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    for f in [*art.iterdir(), *app.glob('*.dat'), *app.glob('*.log')]:
        if f.is_file():
            shutil.copyfile(f, dest/f.name)
    assert all(hashlib.sha256((app/n).read_bytes()).hexdigest() == h for n,h in preserved.items())
    assert (app/'runs.log').read_bytes().startswith(prior_index)
    receipt = dict(passed=failure is None, failure=failure, engine=args.engine, checks=checks,
                   menu_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                   shim_sha256=hashlib.sha256((b/'keys.so').read_bytes()).hexdigest(),
                   VDP_sha256=hashlib.sha256((p/'esp32-firmware.bin').read_bytes()).hexdigest(),
                   prior_reports_preserved=True, physical_test_performed=False,
                   elapsed_seconds=round(time.monotonic()-started,3))
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)
if failure and not args.probe:
    raise SystemExit(1)
