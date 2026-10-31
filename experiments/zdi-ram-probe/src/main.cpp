// Console8 diagnostic only: no flash payload, erase, programming or resume path.
// Explicit Author wiring,2026-10-30: GREEN CLOCK GPIO27, BLUE DATA GPIO26.
#include <Arduino.h>
#include <soc/gpio_struct.h>
#include <cstring>

namespace {
constexpr unsigned kClock = 27, kData = 26;
constexpr uint32_t kPins = (1U << kClock) | (1U << kData);
// F92 on-chip RAM occupies upper:E000..FFFF; F000 is also inside F93 RAM.
// RAM_ADDR_U is explicitly set to B7 only after a verified ZDI halt.
constexpr uint32_t kRam = 0xB7F000;
constexpr size_t kBytes = 64;
bool armed = false, haltRequested = false, ramAttempted = false;
uint8_t original[kBytes], pattern[kBytes], observed[kBytes];

void release() { GPIO.enable_w1tc = kPins; }
unsigned inputs() {
  return ((GPIO.in >> kClock) & 1U) | (((GPIO.in >> kData) & 1U) << 1);
}
void finalState() {
  Serial.printf("PINS out=%08lX enable=%08lX in=%08lX GREEN=%u BLUE=%u\r\n",
                (unsigned long)GPIO.out, (unsigned long)GPIO.enable,
                (unsigned long)GPIO.in, inputs() & 1U, (inputs() >> 1) & 1U);
}
[[noreturn]] void finish(const char* result) {
  release();
  interrupts();
  Serial.printf("PROBE END %s halt_requested=%u ram_attempted=%u flash_operations=0\r\n",
                result, unsigned(haltRequested), unsigned(ramAttempted));
  finalState();
  Serial.flush();
  while (true) delay(1000);
}
void check(bool condition, const char* failure) { if (!condition) finish(failure); }
void writeBit(bool bit) {
  GPIO.out_w1tc = 1U << kClock;
  delayMicroseconds(10);
  if (bit) GPIO.out_w1ts = 1U << kData;
  else GPIO.out_w1tc = 1U << kData;
  GPIO.enable_w1ts = 1U << kData;
  delayMicroseconds(10);
  check(inputs() == (bit ? 2U : 0U), "FAIL local driven-bit LOW-clock check");
  GPIO.out_w1ts = 1U << kClock;
  delayMicroseconds(10);
  check(inputs() == (bit ? 3U : 1U), "FAIL local driven-bit HIGH-clock check");
}
void writeByte(uint8_t value) {
  for (int bit = 7; bit >= 0; --bit) writeBit(value & (1U << bit));
}
uint8_t readByte() {
  uint8_t value = 0;
  for (unsigned bit = 0; bit < 8; ++bit) {
    GPIO.enable_w1tc = 1U << kData;
    GPIO.out_w1tc = 1U << kClock;
    delayMicroseconds(10);
    check(!(inputs() & 1U), "FAIL local read-clock LOW check");
    value = uint8_t((value << 1) | ((GPIO.in >> kData) & 1U));
    GPIO.out_w1ts = 1U << kClock;
    delayMicroseconds(10);
    check(inputs() & 1U, "FAIL local read-clock HIGH check");
  }
  return value;
}
void start(uint8_t reg, bool read) {
  GPIO.out_w1ts = kPins;
  GPIO.enable_w1ts = kPins;
  delayMicroseconds(10);
  check(inputs() == 3U, "FAIL local START check");
  GPIO.out_w1tc = 1U << kData;
  delayMicroseconds(10);
  for (int bit = 6; bit >= 0; --bit) writeBit(reg & (1U << bit));
  writeBit(read);
}
void done() { writeBit(true); release(); delayMicroseconds(100); }
void readRegisters(uint8_t reg, uint8_t count, uint8_t* output) {
  check((reg == 0 && count == 4) || (reg == 3 && count == 1) ||
        (reg == 0x10 && count == 3) || (reg == 0x20 && count == kBytes),
        "FAIL prohibited read range");
  noInterrupts();
  start(reg, true);
  while (count--) {
    writeBit(false);
    if (reg == 0x20) delayMicroseconds(3);
    *output++ = readByte();
  }
  done();
  interrupts();
}
void writeRegisters(uint8_t reg, uint8_t count, const uint8_t* input) {
  check(armed, "FAIL unarmed write");
  check((reg == 0x10 && count == 1 && input[0] == 0x80) ||
        (reg == 0x13 && count == 3) ||
        (reg == 0x16 && count == 1 && (input[0] == 7 || input[0] == 8 || input[0] == 0x87)) ||
        ((reg == 0x24 || reg == 0x25) && count == 1) ||
        (reg == 0x30 && count == kBytes), "FAIL prohibited write register");
  noInterrupts();
  start(reg, false);
  while (count--) {
    writeBit(false);
    if (reg == 0x30) delayMicroseconds(3);
    writeByte(*input++);
  }
  done();
  interrupts();
}
void writeRegister(uint8_t reg, uint8_t value) { writeRegisters(reg, 1, &value); }
uint8_t status() { uint8_t value; readRegisters(3, 1, &value); return value; }
bool validHalted(uint8_t value) {
  // PS0153 Table125: bit7=ZDI_ACTIVE; reserved bits6,1,0 must be zero.
  return (value & 0xC3) == 0x80;
}
uint32_t readPc() {
  writeRegister(0x16, 7);
  uint8_t bytes[3]; readRegisters(0x10, 3, bytes);
  return uint32_t(bytes[0]) | (uint32_t(bytes[1]) << 8) | (uint32_t(bytes[2]) << 16);
}
void setPc(uint32_t address) {
  const uint8_t bytes[] = {uint8_t(address), uint8_t(address >> 8), uint8_t(address >> 16)};
  writeRegisters(0x13, 3, bytes);
  writeRegister(0x16, 0x87);
  check(readPc() == address, "FAIL PC write/readback");
}
void out(uint8_t port, uint8_t value) {
  // Only RAM mapping ports; no flash-controller port is admitted.
  check((port == 0xB5 && value == 0xB7) || (port == 0xB4 && value == 0x80),
        "FAIL prohibited I/O port");
  writeRegister(0x24, value); writeRegister(0x25, 0x3E);
  writeRegister(0x24, port); writeRegister(0x25, 0xD3);
}
void readRam(uint8_t* output) {
  setPc(kRam); ramAttempted = true; readRegisters(0x20, kBytes, output);
}
void writeRam(const uint8_t* input) {
  setPc(kRam); ramAttempted = true; writeRegisters(0x30, kBytes, input);
}
[[noreturn]] void probe() {
  armed = true;
  uint8_t id[4]; readRegisters(0, 4, id);
  Serial.printf("OBSERVED identity=%02X %02X %02X %02X; not an admission gate for this probe\r\n",
                id[0], id[1], id[2], id[3]);
  haltRequested = true;
  Serial.println("SEND one HALT request; RAM remains gated by three status reads");
  writeRegister(0x10, 0x80);
  delay(2);
  bool halted = true;
  for (unsigned i = 0; i < 3; ++i) {
    const uint8_t value = status();
    Serial.printf("HALT STATUS %u/3=%02X valid=%u\r\n", i + 1, value, unsigned(validHalted(value)));
    halted &= validHalted(value);
    delay(10);
  }
  check(halted, "FAIL halted status not verified; NO RAM attempted");
  const uint32_t pc = readPc();
  check(pc != 0xFFFFFF && readPc() == pc && readPc() == pc, "FAIL stable original PC");
  Serial.printf("HALT verified original_PC=%06lX\r\n", (unsigned long)pc);
  writeRegister(0x16, 8); // Set ADL, from upstream agon-recovery.
  writeRegister(0x25, 0xF3); // DI, leave CPU halted throughout.
  const uint8_t initialized = status();
  check(validHalted(initialized) && (initialized & 0x94) == 0x90,
        "FAIL ADL/interrupt status");
  out(0xB5, 0xB7); out(0xB4, 0x80);
  readRam(original); readRam(observed);
  check(memcmp(original, observed, kBytes) == 0, "FAIL stable original RAM");
  for (unsigned pass = 0; pass < 4; ++pass) {
    for (size_t i = 0; i < kBytes; ++i)
      pattern[i] = pass == 0 ? 0 : pass == 1 ? 0xFF : pass == 2 ? uint8_t(i * 37U + 0x55U) : uint8_t(~(i * 37U + 0x55U));
    writeRam(pattern);
    for (unsigned repeat = 0; repeat < 2; ++repeat) {
      readRam(observed);
      check(memcmp(pattern, observed, kBytes) == 0, "FAIL RAM pattern readback; CPU remains halted");
    }
    Serial.printf("RAM pattern%u/4 verified twice at%06lX bytes64\r\n", pass + 1, (unsigned long)kRam);
  }
  writeRam(original); readRam(observed);
  check(memcmp(original, observed, kBytes) == 0, "FAIL original RAM restoration");
  setPc(pc);
  finish("PASS RAM verified and restored; CPU remains halted; reset required");
}
} // namespace

void setup() {
  pinMode(kClock, INPUT_PULLUP); pinMode(kData, INPUT_PULLUP); release();
  Serial.begin(115200); delay(200);
  Serial.println("WROOM CONSOLE8 HALT RAM PROBE v11 GREEN=GPIO27 BLUE=GPIO26 QUIET");
  Serial.println("No flash API/payload; no target access before exact command; no automatic retry/resume");
  finalState();
  Serial.println("WAIT PROBE CONSOLE8 RAM-ONLY");
  char line[40] = {}; size_t used = 0; bool rejected = false;
  const uint32_t begin = millis();
  while (millis() - begin < 300000) {
    if (!Serial.available()) { delay(1); continue; }
    const char ch = Serial.read();
    if (ch == '\n') {
      line[used] = 0;
      if (!rejected && strcmp(line, "PROBE CONSOLE8 RAM-ONLY") == 0) probe();
      finish("FAIL command refused; no target access");
    }
    if (ch < 32 || ch > 126 || used + 1 >= sizeof(line)) rejected = true;
    else if (!rejected) line[used++] = ch;
  }
  finish("FAIL timeout; no target access");
}
void loop() { delay(1000); }
