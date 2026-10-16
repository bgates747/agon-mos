"""Generate a frozen Flexe profile using the canonical launcher factory."""
import hashlib,importlib.util,os,shutil
from pathlib import Path

root=Path(__file__).resolve().parents[2];b=root/'build/uart0-repair'
def prepare_profile(variant,image,suffix=''):
    source=root/'.emulator/uart0-race';p=root/'.emulator'/('uart0-repair-'+variant+('-'+suffix if suffix else ''))
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if (proc/'exe').resolve()==p/'runtime/flexe-agon-emulator.bin':raise RuntimeError('Profile active')
        except (FileNotFoundError,PermissionError):pass
    p.mkdir(parents=True,exist_ok=True);runtime=p/'runtime';runtime.mkdir(exist_ok=True)
    pins={'flexe-agon-emulator.bin':'412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9',
          'flexe-vdp.so':'77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd',
          'mos_platform.bin':'e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a',
          'mos_platform.map':'71c17176a38a93c7d12c6c1738f4a6d85cdc6c1146e3bb95ae6caa5a07f4792f'}
    for name,pin in pins.items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==pin,name
        shutil.copyfile(source/name,runtime/name)
        if name.endswith('.bin'):os.chmod(runtime/name,0o755)
    firmware=(root/'build/uart0-race/firmware' if variant=='original' else b/variant)/'.pio/build/esp32dev'
    for name,src in [('esp32-firmware.bin','firmware.bin'),('esp32-firmware.elf','firmware.elf')]:shutil.copyfile(firmware/src,runtime/name)
    for name,target in [('fab-agon-emulator.bin','flexe-agon-emulator.bin'),('flexe-agon-emulator.bin','flexe-agon-emulator.bin'),('flexe-vdp.so','flexe-vdp.so'),('mos_platform.bin','mos_platform.bin'),('mos_platform.map','mos_platform.map'),('esp32-firmware.bin','esp32-firmware.bin'),('esp32-firmware.elf','esp32-firmware.elf')]:
        f=p/name
        if f.exists() or f.is_symlink():f.unlink()
        f.symlink_to('runtime/'+target)
    (p/'sdcard').mkdir(exist_ok=True)
    f=p/'sdcard.img'
    if f.exists() or f.is_symlink():f.unlink()
    assert image.resolve().is_relative_to(b)
    f.symlink_to(image.resolve())
    (p/'.mos-release').write_text('Experimental MOS3.0.2 UART ABI1.1, matching Console8\n')
    (p/'.mos-release.sha256').write_text(''.join(pins[n]+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')))
    (p/'.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
    spec=importlib.util.spec_from_file_location('canonical_setup',b/'canonical_setup.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
    factory.write_profile_launcher(p,strict_bespoke=True)
    path=p/'fab-agon-emulator';s=path.read_text()
    token='vdp_name="$(< "${profile_dir}/.bespoke-vdp-profile")"'
    assert s.count(token)==1
    extra='''export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
[[ -f "$profile_dir/sdcard.img" ]] || { echo 'Missing owned FAT image' >&2; exit 1; }
mkdir -p "$AGON_FLEXE_ARTIFACTS"
'''
    s=s.replace(token,extra+token)
    token='        --sdcard "${profile_dir}/sdcard" \\\n'
    assert s.count(token)==2
    # Both generated branches retain the explicit MOS/SD selection; strict
    # bespoke guard prevents the stock branch from being used.
    s=s.replace(token,token+'        --sdcard-img "${profile_dir}/sdcard.img" \\\n')
    path.write_text(s);path.chmod(0o755)
    names=['fab-agon-emulator','fab-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf']
    (p/'.runtime.sha256').write_text(''.join(f'{hashlib.sha256((p/n).read_bytes()).hexdigest()}  {n}\n' for n in names))
    return p
