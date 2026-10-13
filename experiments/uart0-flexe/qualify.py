"""Headless Fab/Flexe qualification; exact transcripts, CPU IRQs and MOS return."""
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
build = root / "build/uart0-flexe"
profile = root / ".emulator"
engine = sys.argv[1] if len(sys.argv) > 1 else "jit"
assert engine in ("jit", "interp")
app = profile / "sdcard/uart"
artifacts = profile / "last-run"
artifacts.mkdir(exist_ok=True)
for name in ("result.dat", "rx.dat", "failure.dat"):
    (app / name).unlink(missing_ok=True)
for path in artifacts.iterdir():
    if path.is_file():
        path.unlink()
subprocess.run(["sha256sum", "--check", "--status", ".runtime.sha256"], cwd=profile, check=True)
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", AGON_FLEXE_ENGINE=engine)
started = time.monotonic()
process = None
mapped = False
returned = False
try:
    with (artifacts / "frontend.log").open("w") as log:
        process = subprocess.Popen(["./flexe-agon-emulator", "--precise-interrupts"],
            cwd=profile, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        while time.monotonic()-started < 180:
            if (app / "failure.dat").exists():
                raise RuntimeError("Application failure: " + (app / "failure.dat").read_bytes().hex())
            if process.poll() is not None:
                raise RuntimeError(f"Emulator exited early: {process.returncode}")
            for child in Path("/proc").glob("[0-9]*"):
                try:
                    if os.getpgid(int(child.name)) == process.pid:
                        mapped |= str(profile / "runtime/flexe-vdp.so") in (child / "maps").read_text()
                except (FileNotFoundError, PermissionError, ProcessLookupError):
                    pass
            debug = artifacts / "esp32-uart0.log"
            if (app / "result.dat").exists() and debug.exists():
                after = debug.read_bytes().partition(b"UART0 ASYNC PASS")[2]
                if b"/uart *" in after:
                    returned = True
                    break
            time.sleep(0.1)
        assert returned, "Timed out before successful return to MOS"
finally:
    if process and process.poll() is None:
        for child in Path("/proc").glob("[0-9]*"):
            try:
                if os.getpgid(int(child.name)) == process.pid and (child / "exe").resolve() == (profile / "flexe-agon-emulator.bin").resolve():
                    os.kill(int(child.name), signal.SIGTERM)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    if not returned:
        failure = build / f"failed-{engine}-{time.time_ns()}"
        failure.mkdir()
        for path in [*artifacts.iterdir(), app / "failure.dat"]:
            if path.is_file():
                shutil.copyfile(path, failure / path.name)
assert process.returncode == 0, f"Shutdown failed: {process.returncode}"
assert mapped, "Requested Flexe adapter was not mapped"
report = (app / "result.dat").read_bytes()
assert len(report) == 27 and report[:9] == b"UART0TX1\0", report.hex()
u24 = lambda offset: int.from_bytes(report[offset:offset+3], "little")
assert u24(9) == 192 and u24(12) > 0, report.hex()
assert report[15:17] == b"\0\0", "RX overflow or sticky RX error"
assert [u24(i) for i in (18,21,24)] == [128,4110,128]
assert (app / "rx.dat").read_bytes() == (build / "expected-rx.bin").read_bytes(), "Reply transcript mismatch"
wire = (artifacts / "mos-to-vdp.bin").read_bytes()
expected = (build / "expected-tx.bin").read_bytes()
assert wire.count(expected) == 1, "Missing, duplicated or interleaved queue output"
stats = json.loads((artifacts / "stats.json").read_text())
assert not any(stats[k] for k in ("failed", "unhandled", "unregistered", "unmapped")), stats
assert stats["engine"] == engine, stats
uart = json.loads((artifacts / "uart.json").read_text())
assert uart["tx_irqs"] > 0 and uart["modem_irqs"] > 0, uart
assert uart["tx_drops"] == uart["rx_overruns"] == 0, uart
subprocess.run(["sha256sum", "--check", "--status", ".runtime.sha256"], cwd=profile, check=True)
receipt = dict(engine=engine, elapsed_seconds=round(time.monotonic()-started,3),
    tx_bytes=len(expected), rx_bytes=192, isr_entries=u24(12), sticky_modem_deltas=report[17],
    accepted_lengths=[u24(i) for i in (18,21,24)], returned_to_mos=True,
    graphical_instance_launched=False, mapped_requested_backend=mapped,
    backend=stats, uart=uart,
    runtime_identities=(profile / ".runtime.sha256").read_text().splitlines(),
    transcript_sha256=hashlib.sha256((app / "rx.dat").read_bytes()).hexdigest())
result = build / f"evidence-{engine}"
result.mkdir(exist_ok=True)
for path in artifacts.iterdir():
    if path.is_file():
        shutil.copyfile(path,result/path.name)
for name in ("result.dat","rx.dat"):
    shutil.copyfile(app/name,result/name)
(result / "receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
