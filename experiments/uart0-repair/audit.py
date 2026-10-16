"""Audit the copied driver, linked objects and actual flag-store instructions."""
import hashlib,json,re,subprocess
from pathlib import Path
from patch_driver import repair,ORIGINAL_SHA256
from analyze import analyze
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-repair'
tools=Path.home()/'.platformio/packages/toolchain-xtensa-esp32@8.4.0+2021r2-patch5/bin'
original=(b/'original-uart.c').read_text();assert hashlib.sha256(original.encode()).hexdigest()==ORIGINAL_SHA256
fixed=repair(original);audits={}
for variant in ('before','fixed','candidate'):
    fw=b/variant;source=(fw/'video/uart0_rx_driver.c').read_text()
    plain=source.replace('#include "uart0_race_hooks.h"\n','')
    plain=re.sub(r'^\s*race_(?:after_publish|wait_after_update|after_mask|after_recovery|note_interrupt)\([^;\n]+\);\n','',plain,flags=re.M)
    assert plain==(original if variant=='before' else fixed),variant
    pos=source.index('p_uart->rx_buffer_full_flg = true;')
    end=source.index('UART_EXIT_CRITICAL_ISR(&(uart_context[uart_num].spinlock));',pos)
    entry=source.rfind('UART_ENTER_CRITICAL_ISR(&(uart_context[uart_num].spinlock));',0,end)
    if variant!='before':assert entry<pos<end and 'race_wait_after_update' not in source[entry:end]
    else:assert pos<entry
    if variant!='candidate':
        wait=source.index('race_wait_after_update(uart_num);')
        assert wait<entry if variant=='before' else wait>end
    build=fw/'.pio/build/esp32dev';mapping=(build/'firmware.map').read_text()
    assert 'src/uart0_rx_driver.c.o' in mapping and 'libdriver.a(uart.c.obj)' not in mapping
    symbols=subprocess.check_output([str(tools/'xtensa-esp32-elf-nm'),str(build/'firmware.elf')],text=True)
    for name in ('uart_read_bytes','uart_rx_intr_handler_default'):
        assert len([s for s in symbols.splitlines() if s.endswith(' '+name)])==1,name
    if variant=='candidate':assert 'uart0_race_' not in symbols
    if variant=='fixed':assert not any(s.endswith(' uart0_race_escape') for s in symbols.splitlines())
    dis=subprocess.check_output([str(tools/'xtensa-esp32-elf-objdump'),'-drS',str(build/'firmware.elf')],text=True)
    (b/f'{variant}-linked.dis').write_text(dis)
    m=re.search(r'^[0-9a-f]+ <uart_rx_intr_handler_default>:\n',dis,re.M);assert m
    n=re.search(r'^[0-9a-f]+ <[^>]+>:\n',dis[m.end():],re.M);assert n
    function=dis[m.start():m.end()+n.start()];(b/f'{variant}-ISR.dis').write_text(function)
    # GCC's source-annotated disassembly identifies the real byte store to
    # uart_obj_t.rx_buffer_full_flg (offset28), not just the source line order.
    marker='p_uart->rx_buffer_full_flg = true;';assert function.count(marker)==1
    offset=function.index(marker)
    store=re.search(r'^([0-9a-f]+):[^\n]*\bs8i\s+a\d+, a\d+, 28\s*$',function[offset:],re.M);assert store
    at=offset+store.start();critical=list(re.finditer(r'^([0-9a-f]+):[^\n]*\bcall8\s+[^\n]*<(xPortEnterCriticalTimeout|vPortExitCritical)>',function,re.M))
    previous=[c for c in critical if c.start()<at][-1];following=[c for c in critical if c.start()>at][0]
    assert previous.group(2)==('vPortExitCritical' if variant=='before' else 'xPortEnterCriticalTimeout')
    assert following.group(2)==('xPortEnterCriticalTimeout' if variant=='before' else 'vPortExitCritical')
    if variant=='candidate':
        block=function[at:following.start()];assert re.search(r'\bs32i\s+a\d+, a\d+, 12',block)
    audits[variant]=dict(driver_override_linked=True,original_archive_object_excluded=True,
        blocking_wait_outside_UART_lock=True,rescue_function_linked=variant=='before',full_flag_store=store.group(1),
        preceding_critical_call=dict(address=previous.group(1),function=previous.group(2)),
        following_critical_call=dict(address=following.group(1),function=following.group(2)),
        firmware_sha256=hashlib.sha256((build/'firmware.bin').read_bytes()).hexdigest(),
        driver_source_sha256=hashlib.sha256(source.encode()).hexdigest())
    pins=json.loads((b/f'{variant}-source.json').read_text())
    for name,pin in pins['files'].items():assert hashlib.sha256((fw/name).read_bytes()).hexdigest()==pin,name
# Good payloads with contradictory synchronization or rescue evidence must fail.
data=(b/'checks-fixed-jit-native/attempt-001/reports/race.dat').read_bytes();assert analyze(data)['repaired_without_rescue']
controls=[]
for name,at,value in [('rescue_used',12+160+60,1),('reader_same_core',12+160+88+1,data[12+160+64+1]),('mask_after_reader',12+160+112+2,0),('RX_not_enabled',12+160+56,0x94)]:
    bad=bytearray(data);bad[at]=value;r=analyze(bad)
    assert r['protocol_complete'] and all(c['integrity_passed'] for c in r['cases']) and not r['regression_passed'];controls.append(name)
native=(b/'native/repair.bin').read_bytes();assert native[64:73]==b'MOS\0\1URF1' and native[137]==255
receipt=dict(source_and_link_audit_passed=True,variants=audits,invalid_evidence_controls_rejected=controls,
    original_driver_sha256=ORIGINAL_SHA256,fixed_driver_sha256=hashlib.sha256(fixed.encode()).hexdigest(),
    physical_repair_verified=False,upstream_or_installed_SDK_modified=False)
(b/'audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2),flush=True)
