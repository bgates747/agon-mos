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
build = root / "build/uart0-bench"
profile = root / ".emulator/uart0-bench"
engine = sys.argv[1] if len(sys.argv) > 1 else "jit"
assert engine in ("jit", "interp")
app = profile / "sdcard/uart0"
artifacts = profile / "last-run"
artifacts.mkdir(exist_ok=True)
for name in ("bench.dat", "failure.dat"):
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
            if (app / "bench.dat").exists() and debug.exists():
                after = debug.read_bytes().partition(b"UART0 BENCH RETURN PASS")[2]
                if b"/uart0 *" in after:
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
report = (app / "bench.dat").read_bytes()
expected_info = json.loads((build / "expected.json").read_text())
assert len(report) == 12+8*17 and report[:12] == b"UART0BN1\x01\x00\x08\x00", report.hex()
u24 = lambda offset: int.from_bytes(report[offset:offset+3], "little")
records = []
for n in range(8):
    p=12+n*17
    row=dict(mode=report[p], pair=report[p+1], raw_ticks=u24(p+2), checksum=u24(p+5),
        overlap_iterations=u24(p+8), accepted=u24(p+11), rx_errors=report[p+14],
        modem_deltas=report[p+15], receiver_result=report[p+16])
    assert row["checksum"] == expected_info["work_checksum"], row
    assert row["accepted"] == expected_info["packet_bytes"], row
    assert row["rx_errors"] == row["receiver_result"] == 0, row
    assert row["overlap_iterations"] == 0 if row["mode"] == 0 else row["overlap_iterations"] > 0, row
    records.append(row)
assert sorted((r["pair"],r["mode"]) for r in records) == [(p,m) for p in range(4) for m in range(2)]
wire = (artifacts / "mos-to-vdp.bin").read_bytes()
assert wire.count((build / "expected-packet.bin").read_bytes()) == 8, "Timed payload wire mismatch"
checks = (build / "checks.bin").read_bytes()
for offset in range(0, len(checks), 60):
    assert wire.count(checks[offset:offset+60]) == 8, "Untimed byte-check wire mismatch"
assert b"UART0 BENCH FIXTURE PASS" in wire
stats = json.loads((artifacts / "stats.json").read_text())
assert not any(stats[k] for k in ("failed", "unhandled", "unregistered", "unmapped")), stats
assert stats["engine"] == engine, stats
uart = json.loads((artifacts / "uart.json").read_text())
# This fixture does not force CTS blockage while a session is open. A backend
# can absorb the timed write without a modem IRQ; require real TX IRQ activity.
assert uart["tx_irqs"] > 0, uart
assert uart["tx_drops"] == uart["rx_overruns"] == 0, uart
subprocess.run(["sha256sum", "--check", "--status", ".runtime.sha256"], cwd=profile, check=True)
receipt = dict(engine=engine, elapsed_seconds=round(time.monotonic()-started,3),
    records=records, receiver_bytes_compared=8*expected_info["payload_bytes"],
    corruption_negative_control_passed=True, raw_ticks_are_uncalibrated=True,
    physical_measurement=False, returned_to_mos=True, graphical_instance_launched=False,
    mapped_requested_backend=mapped, backend=stats, uart=uart,
    runtime_identities=(profile / ".runtime.sha256").read_text().splitlines())
result = build / f"evidence-{engine}"
result.mkdir(exist_ok=True)
for path in artifacts.iterdir():
    if path.is_file():
        shutil.copyfile(path,result/path.name)
for name in ("bench.dat",):
    shutil.copyfile(app/name,result/name)
(result / "receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
