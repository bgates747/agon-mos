"""Independent byte/state oracle for matched receiver synchronization tests."""
import json,sys,zlib
from pathlib import Path
u32=lambda b,o:int.from_bytes(b[o:o+4],'little')
crc=zlib.crc32(bytes(((n*157+7)%254)+1 for n in range(4096)))
def analyze(data):
    assert len(data)==332 and data[:9]==b'URFHOST1\x01' and data[10]==2 and data[11]<=2
    result=dict(stage=data[9],completed=data[11],cases=[],receiver_fixed=None,
                natural_stock_failure_reproduced=False,physical_repair_verified=False)
    for mode in range(data[11]):
        r=data[12+160*mode:172+160*mode];assert r[:6]==b'URF1'+bytes([1,mode]) and r[63] in (0,1)
        fixed=bool(r[63])
        if result['receiver_fixed'] is not None:assert result['receiver_fixed']==fixed
        result['receiver_fixed']=fixed
        events=[dict(type=e[0],core=e[1],full_flag=e[2],fifo=e[3],enabled=u32(e,4),raw=u32(e,8),buffered=u32(e,12),stash=u32(e,16),cycles=u32(e,20)) for e in (r[64:88],r[88:112],r[112:136],r[136:160])]
        pub,reader,masked,escape=events
        integrity=u32(r,8)==4096 and u32(r,12)==crc and not u32(r,16) and not r[61] and r[62]==1
        cores=pub['core'] in (0,1) and pub['core']==masked['core'] and reader['core']==1-pub['core'] and r[52]==pub['core'] and r[53]==reader['core']
        common=pub['type']==1 and reader['type']==2 and masked['type']==3 and pub['full_flag']==1 and reader['full_flag']==0 and reader['enabled']&0x101==0x101 and r[54]==1 and r[55]==64 and u32(r,56)&0x101==0x101 and u32(r,20)==7
        normal=r[6]==3 and not r[60] and masked['full_flag']==1 and masked['enabled']&0x101==0 and escape['type']==0
        forced=r[7]==2 and r[6]==4 and r[60]==1 and masked['full_flag']==0 and masked['enabled']&0x101==0 and 0<u32(r,24)<=128 and u32(r,28)&0x101==0 and u32(r,32)&0x101!=0 and u32(r,36)==0 and u32(r,40)==0 and u32(r,48)==0 and escape['type']==4 and escape['enabled']&0x101==0x101
        repaired=normal and r[7]==(5 if mode else 1) and u32(r,24)==0 and u32(r,28)&0x101==0x101 and not u32(r,36) and not u32(r,40) and not u32(r,48)
        expected=repaired if fixed else forced if mode else normal and r[7]==1
        result['cases'].append(dict(mode=mode,receiver_fixed=fixed,outcome=r[7],received=u32(r,8),crc32=f'{u32(r,12):08X}',RX_errors=u32(r,16),MOS_RX_errors=r[61],driver_state=u32(r,20),rescued=bool(r[60]),integrity_passed=bool(integrity),evidence_valid=bool(integrity and cores and common and expected),pre_escape=dict(fifo=u32(r,24),enabled=u32(r,28),raw=u32(r,32),full_flag=u32(r,36),buffered=u32(r,40),stash=u32(r,44),remaining=u32(r,48)),events=events))
    result['protocol_complete']=data[9]==0 and data[11]==2
    result['regression_passed']=result['protocol_complete'] and all(c['evidence_valid'] for c in result['cases'])
    result['baseline_fault_captured']=result['regression_passed'] and result['receiver_fixed'] is False
    result['repaired_without_rescue']=result['regression_passed'] and result['receiver_fixed'] is True
    return result
if __name__=='__main__':print(json.dumps(analyze(Path(sys.argv[1]).read_bytes()),indent=2))
