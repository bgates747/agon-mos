"""Validate retained complete native/Flexe campaigns without rerunning them."""
import argparse
import hashlib
import json
from pathlib import Path

def validate(out,client):
    wire=(out/'mos-to-vdp.bin').read_bytes();reports=out/'reports'
    assert b'NATIVE UART RETURN' in wire and wire.count(b'UART0 STRESS FIXTURE PASS')==5
    assert b'Arthur - UART0 OTIRX EXPERIMENTAL ABI1.2' in wire
    assert b'UART0 STRESS FAIL' not in wire and b'Error executing autoexec' not in wire
    report=(reports/'batch.dat').read_bytes()
    assert len(report)==492 and report[:12]==b'UBTHOST1\x01\x00\x0a\x00'
    u32=lambda b,o:int.from_bytes(b[o:o+4],'little')
    expected=json.loads((client/'expected.json').read_text())
    for i,(batch,hold) in enumerate(expected['cases']):
        row=report[12+i*48:60+i*48]
        assert row[:7]==b'URM1'+bytes([1,64,hold]), ('CRC identity',i)
        assert u32(row,36)==4096 and u32(row,40)==expected['payload_crc32'], ('CRC payload',i)
        assert u32(row,12)==u32(row,24)==0 and row[44]==row[47]==0 and row[45]==1, ('CRC receive/errors',i)
    for n in (1,2,4,8,16):
        report=(reports/f'stress{n}.dat').read_bytes()
        assert len(report)==76 and report[:12]==b'UART0ST1\x01\x00\x04\x00', ('Stress header',n)
        for i,pause in enumerate((0,1,4,8)):
            row=report[12+i*16:28+i*16];packet=(client/f'packet{i}.bin').read_bytes()
            assert row[0]==pause and row[1]==row[2]==32 and row[3]>0, ('Reply counts',n,i)
            assert int.from_bytes(row[4:7],'little')==len(packet), ('Accepted count',n,i)
            assert row[10]==row[12]==0 and row[13]==47, ('RX/order/last token',n,i)
            # These bytes have always been reserved FF padding, not error flags.
            assert row[14:16]==b'\xff\xff', ('Reserved report bytes',n,i)
            assert wire.count(packet)==5, ('Complete stress wire packet',n,i)
    checks=(client/'checks.bin').read_bytes()
    for off in range(0,len(checks),60):
        assert wire.count(checks[off:off+60])==20, ('Receiver compare command',off)
    stats=json.loads((out/'stats.json').read_text());uart=json.loads((out/'uart.json').read_text())
    assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
    assert uart['tx_drops']==uart['rx_overruns']==0
    return dict(passed=True,engine=stats['engine'],CRC_payload_bytes_verified=40960,
                receiver_final_bytes_compared=163840,ordered_full_duplex_replies=640,
                stress_cases=20,CRC_cases=10,wire_bytes=len(wire),
                wire_sha256=hashlib.sha256(wire).hexdigest(),hardware_qualified=False,
                intermediate_payloads_individually_receiver_compared=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--clients',type=Path,required=True)
    a=p.parse_args();result=validate(a.run,a.clients)
    result['original_receipt_sha256']=hashlib.sha256((a.run/'receipt.json').read_bytes()).hexdigest()
    (a.run/'validated-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
