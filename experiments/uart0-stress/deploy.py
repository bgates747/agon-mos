"""Stage the reviewed stress fixture using the shared removable-SD guards.

Only /test/mos-uart0 is writable by this entry point. No firmware is
flashed; the Author manually installs it if the accepted versions changed.
"""
import importlib.util
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "uart0-bench/deploy.py"
spec = importlib.util.spec_from_file_location("uart0_sd_deployment", source)
deployment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deployment)

if __name__ == "__main__":
    deployment.main("/test/mos-uart0", require_human_review=True)
