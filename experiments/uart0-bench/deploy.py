"""Copy a verified package to a new directory on one explicitly identified SD.

Run using this project's .venv on Oryx. Never flash, open serial ports, replace
existing files or touch any emulator profile. --dry-run performs all preflight
checks without creating directories.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mount_identity(mount, uuid):
    result = subprocess.run(
        ["findmnt", "--json", "--mountpoint", str(mount), "-o", "TARGET,SOURCE,FSTYPE,UUID,OPTIONS"],
        check=True, capture_output=True, text=True,
    )
    records = json.loads(result.stdout)["filesystems"]
    require(len(records) == 1, "Expected one exact mount")
    row = records[0]
    require(Path(row["target"]).resolve() == mount, "Mount target changed")
    require(row["uuid"].upper() == uuid.upper(), "SD UUID mismatch")
    require(row["fstype"] == "vfat" and "rw" in row["options"].split(","), "Need writable FAT SD")
    device = json.loads(subprocess.check_output(
        ["lsblk", "--json", "--nodeps", "-o", "PATH,RM,UUID", row["source"]], text=True,
    ))["blockdevices"]
    require(len(device) == 1 and device[0]["rm"], "Expected a removable block device")
    require(device[0]["uuid"].upper() == uuid.upper(), "Block device UUID mismatch")
    return row


def package_files(package):
    require(package.is_dir(), "Package directory missing")
    expected = {}
    for line in (package / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "Invalid hash")
        require(Path(name).name == name and name not in (".", "..", "SHA256SUMS"), "Unsafe filename")
        require(name not in expected, "Duplicate filename")
        source = package / name
        require(source.is_file() and not source.is_symlink(), "Expected plain package file")
        require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, "Package hash mismatch: " + name)
        expected[name] = digest
    require({p.name for p in package.iterdir()} == set(expected) | {"SHA256SUMS"}, "Unlisted package files")
    require(not (package / "SHA256SUMS").is_symlink(), "Unsafe checksum file")
    manifest = json.loads((package / "manifest.json").read_text())
    require(manifest["deployment_path"] == "/test/mos-uart0", "Unexpected destination")
    require(manifest["vdp"]["stock_release"] and manifest["vdp"]["version"] == "2.16.0", "Need stock VDP 2.16.0")
    require({"readme.txt", "vdp-2.16.0.bin", "mos-candidate.bin", "bench.bin", "checks.bin", "flash.bin"} <= set(expected), "Incomplete manual test package")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--mount", required=True, type=Path)
    parser.add_argument("--uuid", required=True)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    package = args.package.resolve(strict=True)
    mount = args.mount.resolve(strict=True)
    require(mount != Path("/"), "Refusing filesystem root")
    require(not args.receipt.exists(), "Receipt already exists")
    require(not args.receipt.resolve().is_relative_to(mount), "Receipt must remain on the host")
    expected = package_files(package)
    identity = mount_identity(mount, args.uuid)
    parent = mount / "test"
    require(not parent.is_symlink(), "Refusing linked test directory")
    target = parent / "mos-uart0"
    require(not target.exists() and not target.is_symlink(), "Test directory already exists; preserve it")
    if args.dry_run:
        print(json.dumps(dict(dry_run=True, target=str(target), files=len(expected)+1, mount=identity), indent=2))
        return
    # Recheck before the first write. mkdir(exist_ok=False) reserves our NEW
    # directory and refuses any competing deployment instead of replacing it.
    mount_identity(mount, args.uuid)
    parent.mkdir(exist_ok=True)
    target.mkdir(exist_ok=False)
    for name in [*expected, "SHA256SUMS"]:
        shutil.copyfile(package / name, target / name)
    os.sync()
    mount_identity(mount, args.uuid)
    subprocess.run(["sha256sum", "--check", "--status", "SHA256SUMS"], cwd=target, check=True)
    receipt = dict(deployed_at=datetime.now(timezone.utc).isoformat(), mount=identity,
                   destination=str(target), package=str(package), files=len(expected)+1,
                   package_manifest_sha256=expected["manifest.json"], verified=True,
                   firmware_flashing_performed=False, operator="Author performs manual flashing/testing")
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
