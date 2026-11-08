/* Finite UART0 short/long checks and matched legacy/counted pull benchmark. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "rom_crc.h"

extern uint8_t rx_context(void), tx_submit(void);
extern void rx_arm(void), legacy_keyboard(void);
uint8_t *rx_destination;
uint24_t rx_capacity;
volatile uint8_t *rx_result;
volatile uint8_t rx_api_code, rx_callbacks, rx_cb_status;
volatile uint24_t rx_cb_count;
const uint8_t *tx_source;
uint24_t tx_length;
volatile uint8_t tx_done;
volatile uint8_t legacy_data[16], legacy_ready;

/* Published RAM witness survives a stopped test, including live borrowed RAM.
   state:1 running,2 failed/resident,3 successful return prepared.
   bytes1..4: method,size-index,repeat,reason. bytes10..12:logical size LE24;
   byte13:useful; byte14:phase(1correctness/2benchmark). No firmware hook. */
volatile uint8_t bench_witness[32];
static uint8_t packet[8100], guarded[8124], file;
static volatile uint8_t *sv;
static uint16_t token;
static uint32_t work_state = 0x12345678UL, work_units, suite_begin;
static const unsigned source_id = 60001;
static const unsigned sizes[] = {4,8,16,32,64,128,256,1024,4096,8092};
#include "run_counter.inc"

static uint8_t sample(unsigned i) {
    return (uint8_t)((i * 157u) ^ ((i >> 8) * 29u) ^ 7u);
}
static void put16(uint8_t *p, unsigned n) {
    p[0] = (uint8_t)n; p[1] = (uint8_t)(n >> 8);
}
static uint16_t get16(const volatile uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)p[1] << 8;
}
static uint24_t get24(const volatile uint8_t *p) {
    return (uint24_t)p[0] | (uint24_t)p[1] << 8 | (uint24_t)p[2] << 16;
}
static void send(const uint8_t *p, unsigned n) {
    mos_puts((const char *)p, n, 0);
}
static int logline(const char *s) {
    puts(s);
    unsigned n = strlen(s);
    return file && mos_fwrite(file, (char *)s, n) == n &&
           mos_fwrite(file, "\r\n", 2) == 2 && ffs_fsync(mos_getfil(file)) == 0;
}
static int open_report(void) {
    unsigned first = first_report();
    if (!first) return 0;
    for (unsigned i = first; i < 10000; ++i) {
        char name[16];
        snprintf(name, sizeof name, "R%04u.log", i);
        uint8_t existing = mos_fopen(name, FA_READ);
        if (existing) { mos_fclose(existing); continue; }
        file = mos_fopen(name, FA_WRITE | FA_CREATE_NEW);
        return file && save_next_report(i + 1);
    }
    return 0;
}
static void work(void) {
    uint32_t x = work_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    work_state = x;
    ++work_units;
}
static int overdue(uint32_t begin) {
    return (uint32_t)(getsysvar_time() - begin) > 240UL ||
           (uint32_t)(getsysvar_time() - suite_begin) > 14400UL;
}
static int reject(uint8_t reason) {
    bench_witness[4] = reason;
    bench_witness[5] = rx_api_code;
    bench_witness[6] = rx_result ? rx_result[0] : 0xff;
    bench_witness[7] = rx_callbacks;
    bench_witness[8] = tx_done;
    return 0;
}
static int poll(uint8_t value) {
    const uint8_t q[] = {23,0,128,value};
    uint32_t begin = getsysvar_time();
    sv[sysvar_gp] = (uint8_t)~value;
    send(q, sizeof q);
    while (sv[sysvar_gp] != value)
        if (overdue(begin)) return reject(1);
    return 1;
}
static unsigned request(uint8_t op, unsigned id, unsigned offset, unsigned n) {
    uint8_t q[19] = {23,0,216,14,0,1,op,0,0,1,0};
    put16(q + 7, ++token); put16(q + 11, id);
    put16(q + 13, offset); put16(q + 17, n);
    legacy_ready = 0;
    if (op == 4) { q[3] = 8; send(q, 13); }
    else send(q, sizeof q);
    return token;
}
static int legacy_reply(unsigned expected, uint8_t kind) {
    uint32_t begin = getsysvar_time();
    while (!legacy_ready) if (overdue(begin)) return reject(11);
    if (legacy_data[4] != 1 || legacy_data[5] != kind ||
        get16(legacy_data + 6) != expected) return reject(12);
    return 1;
}
static int capabilities(void) {
    unsigned expected = request(4, 26, 0, 0);
    if (!legacy_reply(expected, 4) || get16(legacy_data + 8) != 8)
        return reject(13);
    expected = request(4, 27, 0, 0);
    if (!legacy_reply(expected, 4) || get16(legacy_data + 8) != 512)
        return reject(14);
    return 1;
}
static void clear_source(void) {
    const uint8_t q[] = {23,0,160,(uint8_t)source_id,
                         (uint8_t)(source_id >> 8),2};
    send(q, sizeof q);
}
static void prepare(unsigned n) {
    const uint8_t q[] = {23,0,160,(uint8_t)source_id,
                         (uint8_t)(source_id >> 8),0,0,0};
    memcpy(packet, q, sizeof q);
    put16(packet + 6, n);
    for (unsigned i = 0; i < n; ++i) packet[8+i] = sample(i);
}
static int upload(unsigned n, unsigned asynchronous, unsigned useful) {
    uint32_t begin = getsysvar_time();
    if (!asynchronous) send(packet, n + 8);
    else {
        tx_source = packet; tx_length = n + 8; tx_done = 0;
        __asm__ volatile("" ::: "memory");
        uint8_t a = tx_submit();
#if RX6_GUARDED_TX
        if (a) return reject(2);
#else
        (void)a; /* Unmodified RFC25 returns IER-derived A, not status. */
#endif
        while (!tx_done) {
            if (useful) work();
            if (overdue(begin)) return reject(3);
        }
    }
    /* Source release is not drain. Ordinary output serializes this GP after
       the upload; its reply witnesses VDP parsing of the complete upload.
       This endpoint includes GP request/reply, NOT pure UART wire time. */
    return poll(0x62);
}
static int read_chunk(unsigned offset, unsigned n, unsigned useful) {
    rx_destination = guarded + 16 + offset; rx_capacity = n;
    uint8_t before = rx_callbacks;
    rx_arm();
    if (rx_api_code || !rx_result || rx_result[0] != 1) return reject(4);
    request(8, source_id, offset, n);
    uint32_t begin = getsysvar_time();
    while (rx_result[0] == 1) {
        if (useful) work();
        if (legacy_ready) return reject(15); /* Error leaves receive live. */
        if (overdue(begin)) return reject(5);
    }
    if (rx_result[0] != 2 || get24(rx_result + 2) != n ||
        get24(rx_result + 5) != n ||
        rx_callbacks != (uint8_t)(before + 1) || rx_cb_status ||
        rx_cb_count != n) return reject(6);
    return 1;
}
static int check_bytes(unsigned n) {
    for (unsigned i = 0; i < 16; ++i)
        if (guarded[i] != 0xa5 || guarded[n+16+i] != 0xa5) return reject(7);
    for (unsigned i = 0; i < n; ++i)
        if (guarded[16+i] != sample(i)) return reject(8);
    return 1;
}
static int legacy_download(unsigned n, unsigned useful) {
    memset(guarded, 0xa5, n + 32);
    for (unsigned offset = 0; offset < n;) {
        unsigned count = n - offset;
        if (count > 8) count = 8;
        unsigned expected = request(6, source_id, offset, count);
        uint32_t begin = getsysvar_time();
        while (!legacy_ready) {
            if (useful) work();
            if (overdue(begin)) return reject(11);
        }
        if (!legacy_reply(expected, 6)) return 0;
        for (unsigned i = 0; i < count; ++i)
            guarded[16+offset+i] = legacy_data[8+i];
        for (unsigned i = count; i < 8; ++i)
            if (legacy_data[8+i] != 0) return reject(16);
        offset += count;
    }
    return check_bytes(n);
}
static int download(unsigned n, unsigned useful) {
    memset(guarded, 0xa5, n + 32);
    for (unsigned offset = 0; offset < n;) {
        unsigned count = n - offset;
        if (count > 512) count = 512;
        if (!read_chunk(offset, count, useful)) return 0;
        offset += count;
    }
    return check_bytes(n);
}
static int correctness(void) {
    bench_witness[14] = 1;
    for (unsigned k = 0; k < sizeof sizes / sizeof sizes[0]; ++k) {
        unsigned n = sizes[k];
        bench_witness[2] = (uint8_t)k;
        bench_witness[10] = (uint8_t)n;
        bench_witness[11] = (uint8_t)(n >> 8);
        bench_witness[12] = 0;
        char line[96];
        snprintf(line, sizeof line, "RX006 CHECK BEGIN bytes=%u", n);
        if (!logline(line)) return reject(10);
        prepare(n);
        for (unsigned asynchronous = 0; asynchronous < 2; ++asynchronous) {
            clear_source();
            if (!poll(0x61) || !upload(n, asynchronous, asynchronous) ||
                !download(n, 0) || !legacy_download(n, 0)) return 0;
        }
        snprintf(line, sizeof line, "RX006 CHECK PASS bytes=%u tx_methods=2 rx_methods=2", n);
        if (!logline(line)) return reject(10);
    }
    return 1;
}
static int batch(unsigned n, unsigned method, unsigned useful, unsigned repeat) {
    unsigned loops = n <= 256 ? 64 : 16;
    char line[192];
    snprintf(line, sizeof line, "RX006 BEGIN method=%u useful=%u bytes=%u repeat=%u loops=%u",
             method, useful, n, repeat, loops);
    if (!logline(line)) return reject(10);
    bench_witness[1] = (uint8_t)method;
    bench_witness[3] = (uint8_t)repeat;
    bench_witness[10] = (uint8_t)n;
    bench_witness[11] = (uint8_t)(n >> 8);
    bench_witness[12] = 0;
    bench_witness[13] = (uint8_t)useful;
    bench_witness[14] = 2;
    uint32_t begin = getsysvar_time(), previous_work = work_units;
    for (unsigned i = 0; i < loops; ++i) {
        bench_witness[9] = (uint8_t)i;
        if (!(method ? download(n, useful) : legacy_download(n, useful))) return 0;
    }
    uint32_t elapsed = (uint32_t)(getsysvar_time() - begin);
    uint32_t completed = work_units - previous_work;
    uint32_t credited = completed ? completed - 1 : 0;
    unsigned replies = method ? (n+511)/512 : (n+7)/8;
    snprintf(line, sizeof line,
             "RX006 CELL method=%u useful=%u bytes=%u replies=%u repeat=%u loops=%u mos_counts=%lu work=%lu checksum=%08lX",
             method, useful, n, replies, repeat, loops,
             (unsigned long)elapsed, (unsigned long)credited,
             (unsigned long)work_state);
    return logline(line) || reject(10);
}
int main(void) {
    if (rx_context() || installed_crc(RX_MOS_BYTES) != RX_MOS_CRC) {
        puts("RX006 REFUSED wrong pinned MOS/context");
        return 15;
    }
    if (*(volatile uint24_t *)RX_KBVECTOR) {
        puts("RX006 REFUSED application keyboard callback owned");
        return 15;
    }
    sv = (volatile uint8_t *)mos_sysvars();
    uint8_t entry_mode = sv[sysvar_scrMode];
    if (entry_mode & 128) {
        puts("RX006 REFUSED double-buffered entry; owner preselects visible CLI mode");
        return 15;
    }
    putch(12);
    puts("RX006 SHORT/LONG UART0 CHECKS");
    printf("Target: mainboard VDP, Legacy route, unchanged mode %u\n", (unsigned)entry_mode);
    puts("Allow two minutes. Last BEGIN identifies a stall; a stall is failure.");
    suite_begin = getsysvar_time();
    bench_witness[0] = 1;
    const uint8_t normal[] = {23,0,254,0};
    send(normal, sizeof normal);
    if (!poll(0x60) || !open_report()) return 15;
    mos_setkbvector(legacy_keyboard, 0);
    int ok = logline("RX006 START build=" RX_BUILD) &&
             logline("Methods0legacyREAD_BYTES8 1counted512; same immutable source; logical bytes") &&
             logline("Clock=public MOS counts for WHOLE batch, validation included; setup/logging excluded; no CPU percentage") &&
             capabilities() && correctness();
    char mode_line[64];
    snprintf(mode_line, sizeof mode_line, "RX006 MODE entry=%u unchanged=1", (unsigned)entry_mode);
    if (ok) ok = logline(mode_line);
    static const unsigned measured[] = {128,256,1024};
    for (unsigned k = 0; k < sizeof measured / sizeof measured[0] && ok; ++k) {
        unsigned n = measured[k];
        prepare(n); clear_source();
        ok = poll(0x61) && upload(n, 0, 0);
        for (unsigned useful = 0; useful < 2 && ok; ++useful)
            for (unsigned r = 1; r <= 3 && ok; ++r) {
                unsigned first = r & 1;
                ok = batch(n, first, useful, r) && batch(n, first ^ 1, useful, r);
            }
    }
    if (ok) { clear_source(); ok = poll(0x64); }
    if (ok) {
        mos_setkbvector(0, 0);
        const uint8_t cursor[] = {4,23,1,1,23,1,3};
        send(cursor, sizeof cursor);
        ok = logline("RX006 SUITE PASS");
        mos_fclose(file);
        if (ok) { bench_witness[0] = 3; puts("RX006 RETURN PASS"); return 0; }
    }
    /* Do not issue UART output/new transfers after uncertain failure. Static source,
       destination and callbacks remain resident. Save only the first-fault
       record to the already-open report; no UART output or new transfer. */
    bench_witness[0] = 2;
    char failure[96];
    int length = snprintf(failure, sizeof failure,
                          "RX006 FAIL reason=%u phase=%u method=%u api=%u rxstate=%u\r\n",
                          (unsigned)bench_witness[4], (unsigned)bench_witness[14],
                          (unsigned)bench_witness[1], (unsigned)bench_witness[5],
                          (unsigned)bench_witness[6]);
    if (file && length > 0 && (unsigned)length < sizeof failure) {
        mos_fwrite(file, failure, (unsigned)length);
        ffs_fsync(mos_getfil(file));
        mos_fclose(file);
    }
    for (;;) __asm__ volatile("halt" ::: "memory");
}
