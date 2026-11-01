"""Require the shared Pi checkout immediately before an Oryx emulator launch."""
import os
import shlex
import subprocess


def assert_checkout():
    token = os.environ.get("UART0_ORYX_LEASE")
    if not token:
        raise RuntimeError(
            "UART0_ORYX_LEASE is required. Reserve/check out Oryx using "
            "agon-dev-env/cross-agent/vdplet-rollout/README.md first."
        )
    # Use the canonical SSH configuration; scheduling authority stays on Pi.
    shared = "/Agon/mystuff/agon-dev-env"
    command = [
        shared + "/.venv/bin/python",
        shared + "/cross-agent/vdplet-rollout/oryx_lease.py",
        "assert-owner", "--owner", "agon-mos", "--lease", token,
    ]
    subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "raspberrypi", shlex.join(command)],
        check=True,
    )
