"""Reuse the established MOS regression tools in a separate owned profile."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assert sys.argv[1:] in (['profile'],['jit'],['interp'])
mode=sys.argv[1];name='profile' if mode=='profile' else 'qualify'
source=(root/f'experiments/uart0-mos/{name}.py').read_text()
needle='profile = root / ".emulator"'
assert source.count(needle)==1
source=source.replace(needle,'profile = root / ".emulator/uart0-batching-baseline"')
# Keep baseline receipts apart from earlier accepted-ROM evidence.
if mode!='profile':
    source=source.replace('result = build / f"evidence-{engine}"','result = root / "build/uart0-batching" / f"baseline-{engine}"')
    sys.argv=[f'{name}.py',mode]
else:
    profile=root/'.emulator/uart0-batching-baseline'
    for p in Path('/proc').glob('[0-9]*'):
        try:
            if profile.exists() and (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Baseline profile active')
        except (FileNotFoundError,PermissionError):pass
# __file__ is kept at the original location so root selection stays identical.
exec(compile(source,str(root/f'experiments/uart0-mos/{name}.py'),'exec'),{'__file__':str(root/f'experiments/uart0-mos/{name}.py'),'__name__':'__main__'})
