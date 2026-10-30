// Analyzer self-test build: attach ONLY passive analyzer, never an Agon.
// Identity build: only ZDI reads 00h..03h; no memory or control-register writes.
// Neither build has a flash API, MOS payload, or BOOT-button action.
#include <Arduino.h>
#include "driver/gpio.h"
#include "soc/gpio_struct.h"
#include "soc/io_mux_reg.h"
#include "soc/soc.h"

static constexpr uint32_t pins[] = {26, 27};

#ifdef ZDI_IDENTITY_ONLY
static unsigned settling = 10;
static unsigned matches;
struct DriveSample { unsigned expected, output, enabled, input; };
static DriveSample driveSamples[13];
static unsigned driveCount;

static void pauseEdge() { if (settling) delayMicroseconds(settling); }

static void writeBit(bool bit) {
    GPIO.out_w1tc = 1U << 26;
    pauseEdge();
    if (bit) GPIO.out_w1ts = 1U << 27;
    else GPIO.out_w1tc = 1U << 27;
    GPIO.enable_w1ts = 1U << 27;
    pauseEdge();
    if (driveCount < 13) {
        driveSamples[driveCount++] = {unsigned(bit), (GPIO.out >> 26) & 3U,
                                     (GPIO.enable >> 26) & 3U, (GPIO.in >> 26) & 3U};
    }
    GPIO.out_w1ts = 1U << 26;
    pauseEdge();
}

static uint8_t readByte() {
    uint8_t value = 0;
    for (unsigned i = 0; i < 8; ++i) {
        // Release DATA before the falling edge on which the target drives it.
        GPIO.enable_w1tc = 1U << 27;
        GPIO.out_w1tc = 1U << 26;
        pauseEdge();
        value = (value << 1) | ((GPIO.in >> 27) & 1);
        GPIO.out_w1ts = 1U << 26;
        pauseEdge();
    }
    return value;
}

static void readIdentity() {
    uint8_t bytes[4];
    driveCount = 0;
    // Both signals idle HIGH before START. TDI falling with TCK HIGH starts.
    GPIO.out_w1ts = (1U << 26) | (1U << 27);
    GPIO.enable_w1ts = (1U << 26) | (1U << 27);
    pauseEdge();
    GPIO.out_w1tc = 1U << 27;
    pauseEdge();
    // 7-bit address zero, then READ=1. No write-address operation exists.
    for (unsigned i = 0; i < 7; ++i) writeBit(false);
    writeBit(true);
    for (auto &byte : bytes) {
        writeBit(false);  // Byte separator: continue.
        byte = readByte();
    }
    writeBit(true);       // End block read.
    GPIO.enable_w1tc = 1U << 27;
    unsigned id = bytes[0] | (unsigned(bytes[1]) << 8);
    bool valid = id == 7 && bytes[2] == 0xaa;
    matches += valid;
    Serial.printf("READ settling_us=%u raw=%02X %02X %02X %02X id=%04X rev=%02X valid=%u\r\n",
                  settling, bytes[0], bytes[1], bytes[2], bytes[3], id, bytes[2], unsigned(valid));
    Serial.println("TX: desiredData output26_27 enable26_27 input26_27 (bit0=clock, bit1=data)");
    for (unsigned i = 0; i < driveCount; ++i) {
        const auto &s = driveSamples[i];
        Serial.printf("TX%02u desired=%u out=%u en=%u in=%u\r\n", i, s.expected, s.output, s.enabled, s.input);
    }
}

static void pinState() {
    Serial.printf("PINS out=%08lX enable=%08lX in=%08lX mux26=%08lX mux27=%08lX route26=%08lX route27=%08lX\r\n",
                  (unsigned long)GPIO.out, (unsigned long)GPIO.enable, (unsigned long)GPIO.in,
                  (unsigned long)REG_READ(PERIPHS_IO_MUX_GPIO26_U),
                  (unsigned long)REG_READ(PERIPHS_IO_MUX_GPIO27_U),
                  (unsigned long)REG_READ(GPIO_FUNC0_OUT_SEL_CFG_REG + 26 * 4),
                  (unsigned long)REG_READ(GPIO_FUNC0_OUT_SEL_CFG_REG + 27 * 4));
}

static uint8_t readSingle(uint8_t address) {
    driveCount = 0;
    GPIO.out_w1ts = (1U << 26) | (1U << 27);
    GPIO.enable_w1ts = (1U << 26) | (1U << 27);
    pauseEdge();
    GPIO.out_w1tc = 1U << 27;
    pauseEdge();
    for (int i = 6; i >= 0; --i) writeBit(address & (1U << i));
    writeBit(true);
    writeBit(false);
    uint8_t value = readByte();
    writeBit(true);
    GPIO.enable_w1tc = 1U << 27;
    delayMicroseconds(100);
    return value;
}

static void lineDriveControl() {
    struct LineSample { unsigned before, low, released; } samples[5];
    unsigned count = 0;
    const unsigned oldPadDriver = GPIO.pin[27].pad_driver;
    // Hold GREEN low before changing BLUE: no intentional START is sent.
    // The first/last clock edge can still advance an existing transaction.
    GPIO.enable_w1tc = 1U << 27;
    GPIO.out_w1tc = 1U << 26;
    GPIO.enable_w1ts = 1U << 26;
    delayMicroseconds(100);
    GPIO.out_w1tc = 1U << 27;
    GPIO.pin[27].pad_driver = 1;
    for (unsigned i = 0; i < 5; ++i) {
        const unsigned before = (GPIO.in >> 26) & 3U;
        if (before != 2) break;  // GREEN must be LOW, released BLUE HIGH.
        GPIO.enable_w1ts = 1U << 27;
        delayMicroseconds(100);
        const unsigned low = (GPIO.in >> 26) & 3U;
        if (low == 0) delayMicroseconds(100);
        GPIO.enable_w1tc = 1U << 27;
        delayMicroseconds(100);
        const unsigned released = (GPIO.in >> 26) & 3U;
        samples[count++] = {before, low, released};
        if (low != 0 || released != 2) break;
        delay(10);
    }
    // Release BLUE and restore its mode while GREEN is still LOW.
    GPIO.enable_w1tc = 1U << 27;
    GPIO.pin[27].pad_driver = oldPadDriver;
    delayMicroseconds(100);
    GPIO.enable_w1tc = 1U << 26;
    Serial.printf("LINE CONTROL pulses=%u max=5 low_us=200, GREEN held LOW; now both released\r\n", count);
    for (unsigned i = 0; i < count; ++i) {
        const auto &s = samples[i];
        Serial.printf("LINE%u before=%u low=%u released=%u\r\n", i, s.before, s.low, s.released);
    }
    Serial.println("READY");
}

void setup() {
    Serial.begin(115200);
    pinMode(26, INPUT_PULLUP);
    pinMode(27, INPUT_PULLUP);
    delay(200);
    Serial.println("WROOM ZDI IDENTITY ONLY v7 - GPIO26=TCK GPIO27=TDI");
    Serial.printf("MUX26=%08lX MUX27=%08lX INPUT=%u,%u\r\n",
                  (unsigned long)REG_READ(PERIPHS_IO_MUX_GPIO26_U),
                  (unsigned long)REG_READ(PERIPHS_IO_MUX_GPIO27_U),
                  unsigned((GPIO.in >> 26) & 1), unsigned((GPIO.in >> 27) & 1));
    Serial.println("QUIET - pins released with pull-ups; no polling, no BOOT shortcut");
    Serial.println("H=drive clock HIGH idle; Q=release both; S=10us edges; M=1us edges; F=no delay; each read command makes ten ID reads");
    Serial.println("P=pin registers only; T=one slow read with drive trace");
    Serial.println("I=four independent single-byte reads of registers00..03");
    Serial.println("L=weakest output drive; R=restore default drive (clock/data, no clocks)");
    Serial.println("O=DATA open-drain; B=DATA push-pull baseline (clock stays push-pull)");
    Serial.println("C=short BLUE LOW/release control with GREEN held LOW, then both released");
    Serial.println("A=GREEN open-drain clock; Z=GREEN push-pull clock baseline (BLUE unchanged)");
    pinState();
    Serial.println("READY");
}

void loop() {
    if (!Serial.available()) { delay(1); return; }
    int command = Serial.read();
    if (command == 'H') {
        GPIO.out_w1ts = 1U << 26;
        GPIO.enable_w1ts = 1U << 26;
        GPIO.enable_w1tc = 1U << 27;
        Serial.println("IDLE HIGH - no clocks until read command");
    } else if (command == 'Q') {
        GPIO.enable_w1tc = (1U << 26) | (1U << 27);
        Serial.println("QUIET - both released");
    } else if (command == 'P') {
        pinState();
        Serial.println("READY");
    } else if (command == 'C') {
        lineDriveControl();
    } else if (command == 'A' || command == 'Z') {
        GPIO.enable_w1tc = 1U << 26;
        GPIO.out_w1ts = 1U << 26;
        GPIO.pin[26].pad_driver = command == 'A';
        Serial.printf("GREEN mode=%s pad_driver=%u\r\n",
                      command == 'A' ? "open-drain" : "push-pull",
                      unsigned(GPIO.pin[26].pad_driver));
        pinState();
        Serial.println("READY");
    } else if (command == 'O' || command == 'B') {
        // Change electrical mode while released and keep it released afterward.
        // Open-drain HIGH releases DATA to the existing pull-up. Clock/framing
        // and drive strength are unchanged for this controlled comparison.
        GPIO.enable_w1tc = 1U << 27;
        GPIO.out_w1ts = 1U << 27;
        // gpio_set_direction enables output before changing the open-drain
        // bit. Set that bit directly so changing modes never enables DATA.
        GPIO.pin[27].pad_driver = command == 'O';
        Serial.printf("DATA mode=%s pad_driver=%u\r\n",
                      command == 'O' ? "open-drain" : "push-pull",
                      unsigned(GPIO.pin[27].pad_driver));
        pinState();
        Serial.println("READY");
    } else if (command == 'L' || command == 'R') {
        gpio_drive_cap_t strength = command == 'L' ? GPIO_DRIVE_CAP_0 : GPIO_DRIVE_CAP_2;
        esp_err_t clock = gpio_set_drive_capability(GPIO_NUM_26, strength);
        esp_err_t data = gpio_set_drive_capability(GPIO_NUM_27, strength);
        Serial.printf("DRIVE level=%u clock_result=%d data_result=%d\r\n", unsigned(strength), int(clock), int(data));
        pinState();
        Serial.println("READY");
    } else if (command == 'I') {
        settling = 10;
        for (uint8_t address = 0; address < 4; ++address) {
            uint8_t value = readSingle(address);
            Serial.printf("SINGLE address=%02X value=%02X\r\n", address, value);
            delay(10);
        }
        Serial.println("READY");
    } else if (command == 'T') {
        settling = 10;
        matches = 0;
        readIdentity();
        Serial.println("READY");
    } else if (command == 'S' || command == 'M' || command == 'F') {
        settling = command == 'S' ? 10 : command == 'M' ? 1 : 0;
        matches = 0;
        for (unsigned i = 0; i < 10; ++i) { readIdentity(); delay(50); }
        Serial.printf("RESULT valid=%u/10\r\n", matches);
        Serial.println("READY");
    }
}

#else

static uint32_t muxAddress(uint32_t pin) {
    return pin == 26 ? PERIPHS_IO_MUX_GPIO26_U : PERIPHS_IO_MUX_GPIO27_U;
}

static unsigned input(uint32_t pin) {
    return (GPIO.in >> pin) & 1;
}

static void outputTest(uint32_t pin, const char *phase) {
    // Same GPIO matrix output enable and input read used by upstream recovery.
    GPIO.out_w1ts = 1U << pin;
    GPIO.enable_w1ts = 1U << pin;
    delayMicroseconds(100);
    unsigned high = input(pin);
    delay(20);
    GPIO.out_w1tc = 1U << pin;
    delayMicroseconds(100);
    unsigned low = input(pin);
    delay(20);
    GPIO.out_w1ts = 1U << pin;
    GPIO.enable_w1tc = 1U << pin;
    Serial.printf("GPIO%u %s mux=%08lX IE=%u inputHigh=%u inputLow=%u follows=%u\r\n",
                  unsigned(pin), phase, (unsigned long)REG_READ(muxAddress(pin)),
                  unsigned((REG_READ(muxAddress(pin)) >> 9) & 1), high, low,
                  unsigned(high == 1 && low == 0));
}

void setup() {
    Serial.begin(115200);
    delay(200);
    Serial.println("WROOM GPIO INPUT DIAGNOSTIC v1 - ANALYZER ONLY");
    Serial.printf("Chip=%s revision=%u\r\n", ESP.getChipModel(), ESP.getChipRevision());
    for (auto pin : pins) {
        uint32_t saved = REG_READ(muxAddress(pin));
        Serial.printf("GPIO%u initial mux=%08lX outputEnable=%u\r\n",
                      unsigned(pin), (unsigned long)saved,
                      unsigned((GPIO.enable >> pin) & 1));
        outputTest(pin, "initial");
        REG_SET_BIT(muxAddress(pin), FUN_IE);
        outputTest(pin, "input-enabled");
        REG_WRITE(muxAddress(pin), saved);
        pinMode(pin, INPUT_PULLUP);
    }
    Serial.println("DONE - GPIO26/27 released with internal pull-ups; no target commands");
    Serial.flush();
}

void loop() { delay(1000); }
#endif
