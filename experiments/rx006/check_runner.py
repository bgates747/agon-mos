"""Exercise the actual coordinator with fake SDKs; NO device/lease operations."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time
import types
from unittest.mock import patch

root = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=False)
kit = json.loads(Path(sys.argv[2]).read_text())
positive = Path(sys.argv[3]).read_text().replace("0123456789abcdef", kit["build"])
real_run = subprocess.run
results = []

for case in ("success", "nonempty", "lost-put", "corrupt-readback", "lost-app-status", "bad-witness", "owned-callback"):
    base = out / case
    base.mkdir()
    events = []
    server = dict(online=False, files={}, launched=False)

    class Lock:
        def close(self):
            pass

    class Metadata:
        def __init__(self, *args, **kwargs):
            self.lock = Lock()
        def status(self):
            events.append("status")
            if case == "lost-app-status" and server["launched"]:
                raise TimeoutError("manufactured status loss, not a device")
            return dict(online=server["online"])
        def connect(self, **kwargs):
            assert server["online"]
        def make_directory(self, *args, **kwargs):
            events.append("mkdir")
        def entries(self, *args):
            return ["preexisting"] if case == "nonempty" else []
        def rpc(self, op):
            assert op == 11
            events.append("exit")
            server["online"] = False
            return b""

    class Staged:
        def __init__(self, *args, **kwargs):
            pass
        def close(self):
            pass
        def begin(self, op, remote, **kwargs):
            events.append(op + " " + remote)
            if op == "put":
                server["files"][remote] = Path(kwargs["source"]).read_bytes()
                if case == "lost-put":
                    raise OSError("manufactured lost PUT response after acceptance")
            else:
                b = server["files"][remote]
                if case == "corrupt-readback":
                    b = b + b"wrong"
                Path(kwargs["destination"]).write_bytes(b)
            return dict(completed=True)

    def type_line(url, journal, text):
        events.append("type " + text)
        if text == "EMOS sdserve --fast /":
            server["online"] = True
        else:
            assert text == "EXEC " + kit["sd_directory"] + "/suite.txt"
            server["launched"] = True
            server["online"] = True
            server["files"][kit["sd_directory"] + "/R0001.log"] = positive.encode()
            server["files"][kit["sd_directory"] + "/WITNESS.BIN"] = bytes([2 if case == "bad-witness" else 3]) + bytes(31)
            server["files"][kit["sd_directory"] + "/next.txt"] = b"2\r\n"
        return dict(accepted=True)

    def command(argv, **kwargs):
        if len(argv) > 1 and argv[1].endswith("/bench_lease.py"):
            events.append("assert-owner-FAKE")
            return types.SimpleNamespace(returncode=0)
        assert len(argv) > 1 and argv[1] == str(root / "analyze.py"), argv
        return real_run(argv, **kwargs)

    evidence = base / "manufactured-evidence.txt"
    evidence.write_text("Manufactured test control only; never hardware readiness.\n")
    handoff = dict(schema="RX006-OWNER-HANDOFF1", owner="agon-mos", operator="agon-mos",
                   lease="FAKE-NONDEVICE", phase="consumer", url="http://fake.invalid",
                   epoch=time.time(), cli_verified=True, listener_offline=True,
                   input_ready_neutral=True, owner_actor_stopped=True,
                   callback=1 if case == "owned-callback" else 0, backend=0,
                   entry_mode=0, source_id_available=60001,
                   components=dict(emos_rom_sha256=kit["emos_rom_sha256"],
                                   native_vdp_sha256=kit["native_vdp_sha256"]),
                   evidence=[str(evidence)])
    handoff_path = base / "handoff.json"
    handoff_path.write_text(json.dumps(handoff))
    local_kit = base / "kit.json"
    local_kit.write_text(json.dumps(kit))
    modules = {"sdcard": types.SimpleNamespace(Client=Metadata),
               "sdcard_staged": types.SimpleNamespace(Client=Staged),
               "hardware_validation": types.SimpleNamespace(type_line=type_line)}
    error = None
    args = [str(root / "run.py"), "--kit", str(local_kit), "--handoff", str(handoff_path),
            "--lease", "FAKE-NONDEVICE", "--url", "http://fake.invalid", "--out", str(base / "run")]
    with patch.dict(sys.modules, modules), patch.object(sys, "argv", args), \
         patch.object(subprocess, "run", command), patch.object(time, "sleep", lambda _: None):
        try:
            runpy.run_path(str(root / "run.py"), run_name="__main__")
        except (AssertionError, OSError, TimeoutError) as exc:
            error = str(exc)
    assert (error is None) == (case == "success"), (case, error)
    if case == "owned-callback":
        assert not events
    if case in ("nonempty", "lost-put", "corrupt-readback"):
        assert not server["launched"]
    if case == "lost-put":
        assert sum(x.startswith("put ") for x in events) == 1
    if case in ("lost-app-status", "bad-witness"):
        position = next(i for i,x in enumerate(events) if x.startswith("type EXEC"))
        assert "exit" not in events[position+1:]
    assert sum(x.startswith("type EXEC") for x in events) <= 1
    results.append(dict(case=case, expected_pass=case == "success", actual_pass=error is None, error=error, events=events))
(out / "result.json").write_text(json.dumps(dict(kind="Manufactured fake-SDK runner controls; no network, bench or target operations", cases=results), indent=2)+"\n")
print(json.dumps([dict(case=x['case'], passed=True) for x in results], indent=2))
