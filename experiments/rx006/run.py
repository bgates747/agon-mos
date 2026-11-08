"""ONE RX006 consumer invocation after an actual owner-install/stopped handoff.

No flashing, reset, startup edit, replay, serial port or firmware-private address.
Platform owner supplies exact fresh handoff; missing/uncertain state stops work.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--kit", type=Path, required=True)
p.add_argument("--handoff", type=Path, required=True)
p.add_argument("--lease", required=True)
p.add_argument("--url", required=True)
p.add_argument("--out", type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
out.mkdir(parents=True, exist_ok=False)
kit = json.loads(a.kit.read_text())
handoff = json.loads(a.handoff.read_text())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
sdk = Path("/Agon/mystuff/agon-extender/scripts")
assert kit["schema"] == "RX006-KIT1"
assert handoff["schema"] == "RX006-OWNER-HANDOFF1"
assert handoff["owner"] == handoff["operator"] == "agon-mos"
assert handoff["phase"] == "consumer" and handoff["lease"] == a.lease
assert handoff["url"] == a.url
assert -30 <= time.time() - handoff["epoch"] <= 120
for field in ("cli_verified", "listener_offline", "input_ready_neutral", "owner_actor_stopped"):
    assert handoff[field] is True, field
assert handoff["callback"] == handoff["backend"] == 0
assert 0 <= handoff["entry_mode"] < 128
assert handoff["source_id_available"] == 60001
assert handoff["components"]["emos_rom_sha256"] == kit["emos_rom_sha256"]
assert handoff["components"]["native_vdp_sha256"] == kit["native_vdp_sha256"]
assert handoff["evidence"] and all(Path(x).is_file() for x in handoff["evidence"])
for path,checksum in kit["host_inputs"].items():
    assert sha(path) == checksum, path
for name,item in kit["files"].items():
    assert name == Path(name).name and name.lower() != "autoexec.txt"
    assert sha(item["path"]) == item["sha256"]
sys.path.insert(0, str(sdk))
from sdcard import Client as Metadata
from sdcard_staged import Client as Staged
from hardware_validation import type_line

ctl = "/Agon/mystuff/agon-dev-env/cross-agent/olimex-bench/bench_lease.py"
py = "/Agon/mystuff/agon-dev-env/.venv/bin/python"
sequence = 0
started = time.monotonic()
summary = dict(schema="RX006-CONSUMER1", state="prepared", invocation_attempted=False,
               kit_sha256=sha(a.kit), handoff_sha256=sha(a.handoff), steps=[])


def save(path, value):
    temp = path.with_suffix(path.suffix + ".new")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    temp.replace(path)


def own():
    subprocess.run([py, ctl, "assert-owner", "--owner", "agon-mos", "--lease", a.lease],
                   check=True, stdout=subprocess.DEVNULL, timeout=10)
    assert time.monotonic() - started < 420, "Whole consumer budget exceeded"
    for path, checksum in kit["host_inputs"].items():
        assert sha(path) == checksum, path


def step(label, action):
    global sequence
    own()
    sequence += 1
    summary["pending"] = dict(sequence=sequence, label=label)
    save(out / "summary.json", summary)
    value = action()
    save(out / f"{sequence:03d}-{label}.json", value)
    summary["steps"].append(dict(sequence=sequence, label=label))
    summary["pending"] = None
    save(out / "summary.json", summary)
    return value


def command(label, text):
    return step(label, lambda: type_line(a.url, out / (label + "-keys.json"), text))


def online(wanted, seconds):
    client = Metadata(a.url, out / (f"status-{sequence}.json"), timeout=5)
    deadline = time.monotonic() + seconds
    try:
        while True:
            own()
            current = client.status()  # P4 metadata only: no UART probe/HELLO.
            if bool(current["online"]) == wanted:
                return current
            if time.monotonic() >= deadline:
                raise TimeoutError("Listener state not established; no dispatch/retry/reset")
            time.sleep(0.5)
    finally:
        client.lock.close()


def metadata(label, action):
    client = Metadata(a.url, out / (label + "-metadata.json"), timeout=10)
    try:
        client.connect(require_fast=True)
        return action(client)
    finally:
        client.lock.close()


def transfer(label, operation, remote, local):
    client = Staged(a.url, out / (label + "-transfer.json"), timeout=40)
    try:
        if operation == "put":
            return client.begin("put", remote, source=local, activate=True)
        return client.begin("get", remote, destination=local)
    finally:
        client.close()


try:
    command("start-stage-listener", "EMOS sdserve --fast /")
    step("stage-listener-online", lambda: online(True, 30))
    remote = kit["sd_directory"]
    assert remote.startswith("/test/mos-rx006-") and ".." not in remote

    def directory(client):
        client.make_directory(remote, parents=True)
        assert not list(client.entries(remote)), "Nonempty test namespace; preserve it"
        return dict(directory=remote, initially_empty=True)

    step("fresh-directory", lambda: metadata("mkdir", directory))
    for name,item in kit["files"].items():
        step("put-" + name, lambda name=name,item=item: transfer("put-" + name, "put", remote + "/" + name, item["path"]))
        readback = out / ("readback-" + name)
        step("verify-" + name, lambda name=name,readback=readback: transfer("verify-" + name, "get", remote + "/" + name, readback))
        assert sha(readback) == item["sha256"], name
    step("exit-stage-listener", lambda: metadata("stage-exit", lambda c: dict(response=c.rpc(11).hex())))
    step("stage-listener-offline", lambda: online(False, 10))
    # EXIT returns our known top-level listener to its original verified CLI.
    time.sleep(2)
    summary["invocation_attempted"] = True
    command("one-exec", "EXEC " + remote + "/suite.txt")
    step("terminal-listener-online", lambda: online(True, 180))
    for name in ("R0001.log", "WITNESS.BIN", "next.txt"):
        step("get-" + name, lambda name=name: transfer("get-" + name, "get", remote + "/" + name, out / name))
    witness = (out / "WITNESS.BIN").read_bytes()
    assert len(witness) == 32 and witness[0] == 3
    assert (out / "next.txt").read_text().strip() == "2"
    own()
    subprocess.run([sys.executable, str(Path(__file__).with_name("analyze.py")),
                    str(out / "R0001.log"), "--build", kit["build"],
                    "--out", str(out / "analysis.json")], check=True,
                   stdout=(out / "analysis.stdout").open("w"), timeout=10)
    step("exit-terminal-listener", lambda: metadata("terminal-exit", lambda c: dict(response=c.rpc(11).hex())))
    step("terminal-listener-offline", lambda: online(False, 10))
    time.sleep(2)
    summary.update(state="consumer-stopped-pass", elapsed_seconds=time.monotonic()-started,
                   restoration="Owner exact firmware/file/state restoration and real CLI handback still required; lease not released")
    save(out / "summary.json", summary)
except BaseException:
    summary.update(state="failed-stopped-no-replay", error=traceback.format_exc(),
                   elapsed_seconds=time.monotonic()-started,
                   restoration="Pending state preserved; no reset/LOAD/SAVE/EXIT replay. Return actual stopped actor to owner for reconciliation/recovery.")
    save(out / "summary.json", summary)
    raise
