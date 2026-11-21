"""One finite Oryx cell with ordinary SDL keyboard input and passive wire evidence."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

profile = Path(__file__).resolve().parent
last = profile / "last-run"
assert not last.exists()
assert not list((profile / "sdcard").iterdir())
injector = profile.parents[3] / "agon-6502/build/dsk003/sdl_keys.so"
assert sha256(injector.read_bytes()).hexdigest() == (
    "e223b8f55958b78629717a5b957232dbf60fa8606801aeb8263f00bfca8ad37a"
)
fifo = profile / "keys.fifo"
boot_banner = b" MOS Version 3.1.0 RC 3"

def health():
    boost = [int(p.read_text()) for p in Path("/sys/devices/system/cpu/cpufreq").glob("policy*/boost")]
    assert boost and not any(boost), boost
    sensors = Path("/sys/class/hwmon").glob("hwmon*/temp*_input")
    temps = [int(p.read_text()) for p in sensors if (p.parent / "name").read_text().strip() == "k10temp"]
    assert temps and max(temps) < 80000, temps
    available = int(next(l.split()[1] for l in Path("/proc/meminfo").read_text().splitlines()
                         if l.startswith("MemAvailable:")))
    assert available >= 524288, available
    return {"boost": boost, "peak_sensors_mC": max(temps), "available_KiB": available}

def owned(group):
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            if os.getpgid(int(p.name)) == group and (p / "stat").read_text().split(") ", 1)[1][0] != "Z":
                yield int(p.name)
        except (OSError, ValueError, IndexError):
            continue

health_start = health()
os.mkfifo(fifo, 0o600)
fd = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
proc = None
actions = []
error = None
start = time.monotonic()
wire = b""
try:
    with (profile / "frontend.log").open("w") as log:
        proc = subprocess.Popen(
            ["./flexe-agon-emulator", "--precise-interrupts"], cwd=profile,
            env=dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
                     LD_PRELOAD=str(injector), AGON_TEST_KEY_FIFO=str(fifo)),
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        def read_wire():
            path = last / "mos-to-vdp.bin"
            return path.read_bytes() if path.exists() else b""

        def wait_for(predicate):
            while time.monotonic() - start < 90:
                assert proc.poll() is None, "frontend exited before qualification"
                data = read_wire()
                if any(x in data for x in (b"NMI001 REFUSED", b"NMI001 UNEXPECTED RETURN",
                                            b"NMI001 POSTBOOT FAIL", b"NMI001 REUSE FAIL")):
                    raise AssertionError("guest reported a failure")
                if predicate(data):
                    return data
                health()
                time.sleep(0.2)
            raise TimeoutError("initial boot, yield, reboot or postboot witness missed 90 s bound")

        def type_line(line):
            for scan in [*(ord(c) - ord("a") + 4 for c in line), 40]:
                for event in (1, 0):
                    assert os.write(fd, bytes((scan, event))) == 2
                    time.sleep(0.12)
            actions.append({"command": line, "seconds": time.monotonic() - start})

        def prompt_after(data, at):
            return b"/ *" in data[at:] and boot_banner in data[at:]

        wait_for(lambda w: prompt_after(w, 0))
        type_line("nmiproof")
        wire = wait_for(lambda w: b"NMI001 YIELD 8" in w and
                       prompt_after(w, w.index(b"NMI001 YIELD 8")))
        type_line("nmicheck")
        wire = wait_for(lambda w: b"NMI001 POSTBOOT PASS" in w)
        assert re.findall(rb"NMI001 YIELD ([0-9]+)", wire) == [str(i).encode() for i in range(1, 9)]
        assert wire.count(boot_banner) == 2 and b"NMI001 POSTBOOT WDT 20 STATE 0" in wire
except Exception as exc:
    error = repr(exc)
finally:
    os.close(fd)
    fifo.unlink()
    if proc is not None:
        for pid in list(owned(proc.pid)):
            try:
                if Path(f"/proc/{pid}/exe").resolve() == (profile / "runtime/emulator").resolve():
                    os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 12
        while list(owned(proc.pid)) and time.monotonic() < deadline:
            time.sleep(0.1)
        if list(owned(proc.pid)):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)
        assert not list(owned(proc.pid)), "owned processes survived"
    if (last / "mos-to-vdp.bin").exists():
        wire = (last / "mos-to-vdp.bin").read_bytes()
    stats_file = last / "stats.json"
    stats = json.loads(stats_file.read_text()) if stats_file.exists() else {}
    if not error and (not stats or any(stats.get(k) for k in
                                      ("failed", "unhandled", "unregistered", "unmapped"))):
        error = "VDP backend result missing or faulty"
    result = {"passed": not error, "error": error, "physical": False,
              "actions": actions, "yield_markers": [int(v) for v in re.findall(rb"NMI001 YIELD ([0-9]+)", wire)],
              "boot_count": wire.count(boot_banner), "health_start": health_start,
              "duration": time.monotonic() - start, "stats": stats}
    (profile / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
if error:
    raise SystemExit(1)
