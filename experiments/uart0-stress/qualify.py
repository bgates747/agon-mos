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
build = root / "build/uart0-stress"
engine = sys.argv[1] if len(sys.argv) > 1 else "jit"
assert engine in ("jit", "interp")
negative = sys.argv[2] if len(sys.argv) > 2 else None
assert negative in (None, "sequence", "payload")
profile = root / (".emulator/uart0-stress-controls" if negative else ".emulator/uart0-stress")
app = profile / "sdcard/uart0"
artifacts = profile / "last-run"
artifacts.mkdir(exist_ok=True)
for name in ("stress.dat", "failure.dat", "baseline.dat"):
    (app / name).unlink(missing_ok=True)
for path in artifacts.iterdir():
    if path.is_file():
        path.unlink()
subprocess.run(["sha256sum", "--check", "--status", ".runtime.sha256"], cwd=profile, check=True)
if negative:
    # Only the separate disposable controls profile receives a corrupted app.
    original = (build / "test.bin").read_bytes()
    packet = (build / "packet0.bin").read_bytes()
    assert original.count(packet) == 1
    pos = original.index(packet) + (273 if negative == "sequence" else 14)
    changed = bytearray(original)
    changed[pos] ^= 1
    target = app / "test.bin"
    target.write_bytes(changed)
    identities = profile / ".runtime.sha256"
    identities.write_text("".join(
        f"{hashlib.sha256(changed).hexdigest()}  sdcard/uart0/test.bin\n"
        if line.endswith("  sdcard/uart0/test.bin\n") else line
        for line in identities.read_text().splitlines(keepends=True)))
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", AGON_FLEXE_ENGINE=engine)
started = time.monotonic()
process = None
mapped = False
returned = False
rejected = False
try:
    with (artifacts / "frontend.log").open("w") as log:
        process = subprocess.Popen(["./flexe-agon-emulator", "--precise-interrupts"],
            cwd=profile, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        while time.monotonic()-started < 180:
            if (app / "failure.dat").exists() and negative:
                debug = artifacts / "mos-to-vdp.bin"
                if debug.exists() and b"UART0 STRESS FAIL" in debug.read_bytes():
                    rejected = True
                    break
            elif (app / "failure.dat").exists():
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
            if (app / "stress.dat").exists() and debug.exists():
                after = debug.read_bytes().partition(b"UART0 STRESS RETURN PASS")[2]
                if b"/uart0 *" in after:
                    returned = True
                    break
            time.sleep(0.1)
        assert rejected if negative else returned, "Timed out before expected result"
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
    if not returned and not rejected:
        failure = build / f"failed-{engine}-{time.time_ns()}"
        failure.mkdir()
        for path in [*artifacts.iterdir(), app / "failure.dat"]:
            if path.is_file():
                shutil.copyfile(path, failure / path.name)
assert process.returncode == 0, f"Shutdown failed: {process.returncode}"
assert mapped, "Requested Flexe adapter was not mapped"
if negative:
    failure = (app / "failure.dat").read_bytes()
    assert len(failure) == 76 and failure[:9] == b"UART0ST1\x01"
    assert failure[9] == (1 if negative == "sequence" else 2), failure.hex()
    assert failure[24] == (1 if negative == "sequence" else 0), failure.hex()
    wire = (artifacts / "mos-to-vdp.bin").read_bytes()
    assert b"UART0 STRESS FAIL" in wire and b"UART0 STRESS FIXTURE PASS" not in wire
    result = build / f"evidence-control-{negative}"
    result.mkdir(exist_ok=True)
    shutil.copyfile(app / "failure.dat", result / "failure.dat")
    receipt = dict(control=negative, rejected=True, failure_stage=failure[9],
        sequence_error=failure[24], elapsed_seconds=round(time.monotonic()-started,3),
        test_sha256=hashlib.sha256((app / "test.bin").read_bytes()).hexdigest(),
        separate_profile=True, graphical_instance_launched=False)
    (result / "receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
    sys.exit(0)
report = (app / "stress.dat").read_bytes()
expected_info = json.loads((build / "expected.json").read_text())
assert len(report) == 76 and report[:12] == b"UART0ST1\x01\x00\x04\x00", report.hex()
records=[]
for n,pause in enumerate((0,1,4,8)):
    row=report[12+n*16:28+n*16]
    record=dict(pause_frames=row[0], expected_replies=row[1], observed_replies=row[2],
        replies_while_busy=row[3],accepted=int.from_bytes(row[4:7],"little"),
        raw_ticks=int.from_bytes(row[7:10],"little"),rx_errors=row[10],modem_deltas=row[11],
        sequence_error=row[12],last_token=row[13])
    assert record["pause_frames"]==pause and row[1]==row[2]==32 and row[3]>0, record
    assert record["accepted"]==expected_info["packet_bytes"][n], record
    assert row[10]==row[12]==row[14]==row[15]==0 and row[13]==47, record
    records.append(record)
wire=(artifacts/"mos-to-vdp.bin").read_bytes()
for n in range(4):
    packet=(build/f"packet{n}.bin").read_bytes()
    assert wire.count(packet)==1, f"Case {n} wire bytes differ"
checks=(build/"checks.bin").read_bytes()
for offset in range(0,len(checks),60):
    assert wire.count(checks[offset:offset+60])==4, "Receiver comparator missing"
cursor=wire.index(b"Setup PASS: bad-byte detection and good-byte check.")
for n in range(4):
    markers=[f"Case {n+1}/4: ".encode(),b"Ordered replies PASS; TX drained;"]
    markers += [f"Receiver verification {q}/4 complete".encode() for q in range(1,5)]
    markers += [b"Case PASS"]
    for marker in markers:
        cursor=wire.index(marker,cursor)+len(marker)
assert b"\x16\x00\x0cUART0 PAUSE / FULL-DUPLEX TEST" in wire
assert b"If this takes longer than 2 minutes, something is wrong." in wire
assert b"UART0 STRESS FIXTURE PASS" in wire and b"UART0 STRESS FAIL" not in wire
baseline=(app/"baseline.dat").read_bytes()
assert len(baseline)==3 and baseline[0]==baseline[2]==0
stats=json.loads((artifacts/"stats.json").read_text())
assert not any(stats[k] for k in ("failed","unhandled","unregistered","unmapped")), stats
assert stats["engine"]==engine
uart=json.loads((artifacts/"uart.json").read_text())
assert uart["tx_irqs"]>0 and uart["tx_drops"]==uart["rx_overruns"]==0,uart
subprocess.run(["sha256sum","--check","--status",".runtime.sha256"],cwd=profile,check=True)
receipt=dict(engine=engine,elapsed_seconds=round(time.monotonic()-started,3),records=records,
    receiver_bytes_compared=32768,ordered_reply_count=128,replies_observed_before_tx_drain=True,
    corruption_negative_control_passed=True,startup_clear_and_expectation_verified=True,
    ordered_progress_breadcrumbs_verified=True,baseline_diagnostics=list(baseline),
    physical_measurement=False,physical_cts_headroom_qualified=False,
    cts_blockage_proven_by_software_fixture=False,raw_ticks_are_uncalibrated=True,
    returned_to_mos=True,graphical_instance_launched=False,mapped_requested_backend=mapped,
    backend=stats,uart=uart,runtime_identities=(profile/".runtime.sha256").read_text().splitlines())
result=build/f"evidence-{engine}"
result.mkdir(exist_ok=True)
for path in artifacts.iterdir():
    if path.is_file(): shutil.copyfile(path,result/path.name)
for name in ("stress.dat","baseline.dat"): shutil.copyfile(app/name,result/name)
(result/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
