"""Capture a native stall through the frozen debugger, without changing code.

Run on Oryx using the project venv. Only the dedicated auto profile is used;
each attempt retains its transcript, debugger state and runtime identities.
"""
import json
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
profile = root / '.emulator/uart0-ab-auto'
art = profile / 'last-run'
base = root / 'build/uart0-ab/debug-stalls'
base.mkdir(exist_ok=True)
for procdir in Path('/proc').glob('[0-9]*'):
    try:
        if (procdir / 'exe').resolve() == (profile / 'runtime/flexe-agon-emulator.bin').resolve():
            raise RuntimeError('Auto profile is already running')
    except (FileNotFoundError, PermissionError):
        pass
subprocess.run(['sha256sum', '--check', '--status', '.runtime.sha256'], cwd=profile, check=True)
engine = sys.argv[1] if len(sys.argv) > 1 else 'jit'
assert engine in ('jit', 'interp')
attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 4
precise = len(sys.argv) < 4 or sys.argv[3] != 'coarse'
for attempt in range(attempts):
    number = 1
    while (base / f'attempt-{number:03d}').exists():
        number += 1
    dest = base / f'attempt-{number:03d}'
    dest.mkdir()
    for f in [*art.iterdir(), *(profile / 'sdcard/uart0').glob('*.dat')]:
        if f.is_file():
            f.unlink()
    master, slave = pty.openpty()
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               AGON_FLEXE_ENGINE=engine, TERM='xterm')
    proc = subprocess.Popen(['./fab-agon-emulator', '--debugger'] + (['--precise-interrupts'] if precise else []),
                            cwd=profile, env=env, stdin=slave, stdout=slave, stderr=slave,
                            start_new_session=True)
    os.close(slave)
    transcript = bytearray()

    def read_for(seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if select.select([master], [], [], min(.1, deadline-time.monotonic()))[0]:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                transcript.extend(chunk)

    started = changed = time.monotonic()
    size = -1
    reason = 'deadline'
    data = b''
    try:
        while time.monotonic() - started < 180:
            read_for(.25)
            path = art / 'mos-to-vdp.bin'
            data = path.read_bytes() if path.exists() else b''
            if b'UART0 AB MOS RETURN' in data:
                reason = 'returned'
                break
            if len(data) != size:
                size = len(data)
                changed = time.monotonic()
            if time.monotonic() - changed > 15:
                reason = 'no_tx_progress'
                break
            if proc.poll() is not None:
                reason = 'exited'
                break
        if proc.poll() is None:
            os.write(master, b'\x03')
            read_for(1)
            # Fixed address ranges cover this native image's dispatch/data,
            # four kernels/descriptors and stack. Maps are retained alongside.
            commands = ['state', 'registers', 'mem 040300 200',
                        'mem 047900 1c00', 'mem 0bfe80 180',
                        'dis24 0402c0 040310']
            for cmd in commands:
                os.write(master, cmd.encode() + b'\r')
                read_for(.4)
            if reason != 'returned':
                os.write(master, b'c\r')
                read_for(2)
                os.write(master, b'\x03')
                read_for(.5)
                for cmd in ['state', 'registers', 'mem 040460 40']:
                    os.write(master, cmd.encode() + b'\r')
                    read_for(.4)
            os.write(master, b'exit\r')
            read_for(1)
            proc.wait(timeout=10)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=10)
        os.close(master)
        (dest / 'debugger.log').write_bytes(transcript)
        for f in [*art.iterdir(), *(profile / 'sdcard/uart0').glob('*.dat')]:
            if f.is_file():
                shutil.copyfile(f, dest / f.name)
        shutil.copyfile(profile / '.runtime.sha256', dest / 'runtime.sha256')
        for name in ['app.map', 'app.lst', 'test.bin']:
            shutil.copyfile(root / 'build/uart0-ab/native' / name, dest / name)
        outcome = dict(engine=engine, precise_interrupts=precise, reason=reason, elapsed_seconds=time.monotonic()-started,
                       tx_bytes=len(data), last_phase=repr(data.split(b'A/B repeat')[-1][:32]),
                       exit_code=proc.returncode)
        (dest / 'outcome.json').write_text(json.dumps(outcome, indent=2)+'\n')
        print(json.dumps(dict(artifact_directory=str(dest.relative_to(root)), **outcome)), flush=True)
    if reason != 'returned':
        break
