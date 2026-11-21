/* Private controls for the isolated NMI-001 firmware. */
#include <stdint.h>
#include <stdio.h>

extern uint8_t nmi_proof_state;
extern uint8_t nmi_read_watchdog(void);
extern void nmi_proof_run(void);

#define WDT_ENABLED 0x80
#define WDT_RESET_CAUSE 0x20
#define WITNESS ((volatile uint8_t *)0x05ed00)
#define APP_REUSE ((volatile uint8_t *)0x050000)

int nmi_proof_command(char *args) {
    (void)args;
    if (nmi_proof_state || (nmi_read_watchdog() & WDT_ENABLED)) {
        puts("NMI001 REFUSED");
        return 19;
    }
    for (unsigned i = 0; i < 5; ++i)
        WITNESS[i] = 0;
    puts("NMI001 START");
    nmi_proof_run();
    puts("NMI001 UNEXPECTED RETURN");
    return 19;
}

void nmi_proof_host(unsigned count) {
    printf("NMI001 YIELD %u\r\n", count);
}

int nmi_check_command(char *args) {
    (void)args;
    uint8_t wdt = nmi_read_watchdog();
    printf("NMI001 POSTBOOT WDT %02X STATE %u\r\n", wdt, nmi_proof_state);
    if (nmi_proof_state || wdt != WDT_RESET_CAUSE ||
        WITNESS[0] != 'N' || WITNESS[1] != 'M' || WITNESS[2] != 'I' ||
        WITNESS[3] != 8 || WITNESS[4] != 8) {
        puts("NMI001 POSTBOOT FAIL");
        return 19;
    }
    APP_REUSE[0] = 0x5a;
    APP_REUSE[1] = 0xa5;
    if (APP_REUSE[0] != 0x5a || APP_REUSE[1] != 0xa5 ||
        (nmi_read_watchdog() & WDT_ENABLED)) {
        puts("NMI001 REUSE FAIL");
        return 19;
    }
    WITNESS[0] = 0;
    puts("NMI001 POSTBOOT PASS");
    return 0;
}
