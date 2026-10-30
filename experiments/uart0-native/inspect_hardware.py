"""Read new numbered native MOS runs from a workspace capture, never the live card."""
import argparse,hashlib,json,re
from pathlib import Path

def inspect(directory,minimum_run=30,emulator=False):
    expected_crc='3448E183' if emulator else '5B36B5B1'
    rows=[];passed=[]
    for path in sorted(directory.glob('R[0-9][0-9][0-9][0-9].log')):
        number=int(path.stem[1:])
        if number<minimum_run:continue
        text=path.read_text();tests=dict(re.findall(r'^TEST (\d+) (PASS|FAIL|SKIP|PENDING)$',text,re.M))
        finish=re.search(rf'^END run={number:04} (PASS|FAIL|SKIP|PENDING)$',text,re.M)
        row=dict(run=number,status=finish[1] if finish else 'INCOMPLETE',tests=tests)
        if tests.get('3')=='PASS':
            assert f'MOS_ROM128K_CRC32={expected_crc} API=1.2' in text, 'Wrong installed MOS in passed native test'
            data=(directory/f'S{number:04}.dat').read_bytes()
            assert len(data)==76 and data[:12]==b'UART0ST1\x01\0\x04\0'
            witness=re.search(rf'^REPORT S{number:04}\.dat hex=([0-9A-F]+)$',text,re.M)
            assert witness and bytes.fromhex(witness[1])==data,'Binary/journal mismatch'
            for i,(pause,length) in enumerate(zip((0,1,4,8),(8582,8585,8594,8606))):
                r=data[12+i*16:28+i*16]
                assert r[0]==pause and r[1]==r[2]==32 and 0<r[3]<=32
                assert int.from_bytes(r[4:7],'little')==length
                assert r[10]==r[12]==0 and r[13]==47 and r[14:16]==b'\xff\xff'
            assert len((directory/f'P{number:04}.dat').read_bytes())==3
            row.update(native_stress_verified=True,ordered_replies=128,final_receiver_bytes_compared=32768)
            passed.append(number)
        rows.append(row)
    return dict(report_version=1,physical_capture=not emulator,expected_MOS_ROM_CRC32=expected_crc,
                runs=rows,native_stress_pass_runs=passed,repeat_verified=len(passed)>=2,
                electrical_CTS_margin_qualified=False,intermediate_receiver_payloads_individually_compared=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path);p.add_argument('--minimum-run',type=int,default=30)
    p.add_argument('--emulator',action='store_true')
    a=p.parse_args();print(json.dumps(inspect(a.directory,a.minimum_run,a.emulator),indent=2))
