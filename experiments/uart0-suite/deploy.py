"""Refresh the stable UART0 SD directory, preserving history in workspace."""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('uart0_sd',root/'experiments/uart0-bench/deploy.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
require=shared.require

def selected_mount(mount,uuid):
    # A cloned FAT UUID is ambiguous even if only one clone is mounted now.
    devices=json.loads(subprocess.check_output(
        ['lsblk','--json','--list','-o','PATH,UUID,RM'],text=True))['blockdevices']
    matches=[d for d in devices if (d.get('uuid') or '').upper()==uuid.upper()]
    require(len(matches)==1 and matches[0]['rm'],'SD UUID is missing or ambiguous')
    return shared.mount_identity(mount,uuid)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('package',type=Path);p.add_argument('--mount',required=True,type=Path)
    p.add_argument('--uuid',required=True);p.add_argument('--backup',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path);p.add_argument('--previous-manifest-sha256')
    scope=p.add_mutually_exclusive_group()
    scope.add_argument('--exploratory-uart0-ab',action='store_true',help='Author-authorized physical A/B comparison despite known emulator receiver race')
    scope.add_argument('--exploratory-receiver-recovery',action='store_true',help='Author-authorized unchanged-VDP Console8 receiver investigation')
    p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    package=a.package.resolve(strict=True);mount=a.mount.resolve(strict=True)
    backup=a.backup.resolve();receipt=a.receipt.resolve()
    require(backup.is_relative_to(root/'build/uart0-suite'),'Backup must be in suite workspace')
    require(not backup.exists() and not receipt.exists(),'Workspace backup/receipt already exists')
    require(not backup.is_relative_to(mount) and not receipt.is_relative_to(mount),'Evidence must stay off-card')
    expected=shared.package_files(package)
    manifest=json.loads((package/'manifest.json').read_text())
    exploratory=(manifest.get('exploratory_hardware') is True
        and manifest.get('menu_integration_passed') is True
        and bool(manifest.get('hardware_test_authorization'))
        and ((a.exploratory_uart0_ab and manifest.get('experiment')=='uart0-ab')
            or (a.exploratory_receiver_recovery and manifest.get('experiment')=='uart0-recovery'
                and manifest.get('fixture_checks_passed') is True)))
    require(manifest.get('suite') is True and (manifest.get('automated_qualification_passed') is True or exploratory),'Need a qualified suite or explicitly authorized exploratory UART0 investigation')
    identity=selected_mount(mount,a.uuid)
    parent=mount/'test';target=parent/'mos-uart0'
    require(not parent.is_symlink() and not target.is_symlink(),'Linked destination refused')
    old_names=set();old_hashes={};preserve=[]
    if target.exists():
        require(target.is_dir() and a.previous_manifest_sha256,'Existing target needs exact prior manifest identity')
        require(hashlib.sha256((target/'manifest.json').read_bytes()).hexdigest()==a.previous_manifest_sha256,'Prior manifest changed')
        old=json.loads((target/'manifest.json').read_text())
        require(old['deployment_path']=='/test/mos-uart0','Unexpected previous target')
        require(hashlib.sha256((target/'test.bin').read_bytes()).hexdigest()==old['files']['test.bin']['sha256'],'Filename collision: unrecognized test.bin')
        old_names=set(old['files'])|{'manifest.json','SHA256SUMS'}
        for path in target.iterdir():
            require(path.is_file() and not path.is_symlink(),'Unexpected directory/link in active fixture')
            old_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            if path.name not in old_names:
                require(path.name not in expected and path.name!='SHA256SUMS','Operator filename collision: '+path.name)
                if path.name not in {'baseline.dat','bench.dat','stress.dat','failure.dat','integrated.dat'}:preserve.append(path.name)
    if a.dry_run:
        print(json.dumps(dict(dry_run=True,target=str(target),backup=str(backup),preserve=preserve,mount=identity),indent=2));return
    # First preserve all previous files on host; do not create SD history dirs.
    backup.mkdir(parents=True,exist_ok=False)
    for name,digest in old_hashes.items():
        shutil.copyfile(target/name,backup/name)
        require(hashlib.sha256((backup/name).read_bytes()).hexdigest()==digest,'Workspace backup mismatch')
        require(hashlib.sha256((target/name).read_bytes()).hexdigest()==digest,'SD changed during backup')
    selected_mount(mount,a.uuid)
    parent.mkdir(exist_ok=True);target.mkdir(exist_ok=True)
    for name in old_hashes:
        if name not in preserve and name not in expected and name!='SHA256SUMS':(target/name).unlink()
    # Install the executable last; the card remains on the host throughout.
    for name in [*(n for n in expected if n!='test.bin'),'SHA256SUMS','test.bin']:
        shutil.copyfile(package/name,target/name)
    os.sync();selected_mount(mount,a.uuid)
    subprocess.run(['sha256sum','--check','--status','SHA256SUMS'],cwd=target,check=True)
    r=dict(deployed_at=datetime.now(timezone.utc).isoformat(),destination=str(target),mount=identity,
        package_manifest_sha256=expected['manifest.json'],verified=True,workspace_backup=str(backup),
        old_file_hashes=old_hashes,preserved_operator_and_numbered_results=preserve,
        physical_firmware_writes=False,sd_history_directory_created=False,
        human_emulator_review_passed=manifest.get('human_review_passed',False),
        exploratory_hardware_comparison=exploratory,
        staging_authorized_by=manifest['hardware_test_authorization'] if exploratory else 'Author remounted card and invited file deployment after the temporary hold')
    with receipt.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r,indent=2))

if __name__=='__main__':main()
