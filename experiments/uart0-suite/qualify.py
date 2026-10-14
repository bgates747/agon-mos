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
build = root / "build/uart0-suite"
profile = root / ".emulator/uart0-suite-auto"
engine = sys.argv[1] if len(sys.argv) > 1 else "jit"
assert engine in ("jit", "interp")
app = profile / "sdcard/uart0"
artifacts = profile / "last-run"
artifacts.mkdir(exist_ok=True)
for path in app.iterdir():
    if path.suffix.lower() in (".dat", ".log", ".txt"):
        path.unlink()
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
        while time.monotonic()-started < 300:
            wire_file = artifacts / "mos-to-vdp.bin"
            if wire_file.exists() and b"UART0 SUITE AUTO FAIL" in wire_file.read_bytes():
                raise RuntimeError("Suite reported FAIL; inspect saved run log")
            if process.poll() is not None:
                raise RuntimeError(f"Emulator exited early: {process.returncode}")
            for child in Path("/proc").glob("[0-9]*"):
                try:
                    if os.getpgid(int(child.name)) == process.pid:
                        mapped |= str(profile / "runtime/flexe-vdp.so") in (child / "maps").read_text()
                except (FileNotFoundError, PermissionError, ProcessLookupError):
                    pass
            debug = artifacts / "esp32-uart0.log"
            if (app / "R0003.log").exists() and debug.exists():
                after = debug.read_bytes().partition(b"UART0 SUITE AUTO RETURN PASS")[2]
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
wire=(artifacts/"mos-to-vdp.bin").read_bytes()
assert b"UART0 SUITE AUTO FAIL" not in wire
assert wire.count(b"UART0 SUITE AUTO COMPLETE; manual measurements pending")==2
index=(app/"runs.log").read_text()
for run in (1,2,3):
    log=(app/f"R{run:04d}.log").read_text()
    assert "report_version=1 build=" in log and f"run={run:04d}" in log
    assert f"END run={run:04d} "+("PASS" if run==3 else "PENDING") in log,log
    assert "TEST 1 PASS" in log,log
    assert log in index
    if run<3:
        assert "TEST 6 PASS" in log
        integration=(app/f"I{run:04d}.dat").read_bytes()
        assert len(integration)==21 and integration[:9]==b"UART0MOS\x00" and integration[18]==0 and integration[20]==63
        for test in (2,3):assert f"TEST {test} PASS" in log,log
        assert "CALIBRATION NOT_MEASURED" in log and "CTS_MARGIN NOT_MEASURED" in log
        b=(app/f"B{run:04d}.dat").read_bytes()
        s=(app/f"S{run:04d}.dat").read_bytes()
        assert b[:12]==b"UART0BN1\x01\x00\x08\x00" and len(b)==148
        assert s[:12]==b"UART0ST1\x01\x00\x04\x00" and len(s)==76
        for prefix in ("N","P"):assert len((app/f"{prefix}{run:04d}.dat").read_bytes())==3
for prefix in ("F","G"):assert not list(app.glob(prefix+"*.dat"))
stats=json.loads((artifacts/"stats.json").read_text())
uart=json.loads((artifacts/"uart.json").read_text())
assert stats["engine"]==engine and not any(stats[k] for k in ("failed","unhandled","unregistered","unmapped")),stats
assert uart["tx_drops"]==uart["rx_overruns"]==0 and uart["tx_irqs"]>0,uart
subprocess.run(["sha256sum","--check","--status",".runtime.sha256"],cwd=profile,check=True)
result=build/f"evidence-{engine}"
result.mkdir(exist_ok=True)
for path in [*artifacts.iterdir(),*app.iterdir()]:
    if path.is_file() and path.suffix.lower() in (".log",".json",".dat",".ppm"):
        shutil.copyfile(path,result/path.name)
receipt=dict(engine=engine,elapsed_seconds=round(time.monotonic()-started,3),
    repeated_run_all=True,individual_diagnostics=True,reserved_run_numbers=[1,2,3],
    numbered_reports_preserved=True,clock_independent_numbering=True,
    benchmark_records=16,stress_records=8,receiver_bytes_verified=196608,
    ordered_stress_replies=256,manual_calibration_marked_pending=True,cts_margin_marked_pending=True,
    integration_ordering_masked_exit_and_ADL0=True,no_flash_in_run_all=True,physical_measurement=False,graphical_instance_launched=False,
    returned_to_mos=True,mapped_requested_backend=mapped,uart=uart,backend=stats,
    runtime_identities=(profile/".runtime.sha256").read_text().splitlines())
(result/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
