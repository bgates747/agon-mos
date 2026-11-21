"""Place the private proof in an isolated export of the pinned RC3 source."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tarfile

BASE = "97311c437093e416342a6c836cf9914f2ced027d"
HERE = Path(__file__).resolve().parent


def replace_once(path, old, new):
    data = path.read_bytes()
    assert data.count(old) == 1, (path, old)
    path.write_bytes(data.replace(old, new))


def prepare(repo, output):
    output.mkdir(parents=True, exist_ok=False)
    with subprocess.Popen(
        ["git", "-C", str(repo), "archive", BASE], stdout=subprocess.PIPE
    ) as git:
        with tarfile.open(fileobj=git.stdout, mode="r|") as archive:
            archive.extractall(output, filter="data")
        if git.wait():
            raise RuntimeError("Cannot export pinned RC3 source")

    for name in ("nmi_proof.asm", "nmi_proof_cli.c"):
        shutil.copyfile(HERE / name, output / "src" / name)
    replace_once(
        output / "src/reset.asm",
        b"ram_nmi_handler:\n\t\tjp __default_nmi_handler",
        b".extern _nmi_proof_dispatch\nram_nmi_handler:\n\t\tjp _nmi_proof_dispatch",
    )
    replace_once(
        output / "src/init.asm",
        b"section .text\n__init:\n",
        b"section .text\n.extern _nmi_proof_reset_only\n__init:\n"
        b"\t\tin0 a,(0x93)\n\t\tbit 7,a\n\t\tjp nz,_nmi_proof_reset_only\n",
    )
    c_file = output / "src/mos.c"
    replace_once(
        c_file,
        b'#include "clock.h"\r\n',
        b'#include "clock.h"\r\n'
        b'extern int nmi_proof_command(char *);\r\n'
        b'extern int nmi_check_command(char *);\r\n',
    )
    replace_once(
        c_file,
        b'\t{ "Obey",',
        b'\t{ "NmiProof", &nmi_proof_command, false, NULL, NULL },\r\n'
        b'\t{ "NmiCheck", &nmi_check_command, false, NULL, NULL },\r\n'
        b'\t{ "Obey",',
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eirene_repo", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prepare(args.eirene_repo, args.output)
