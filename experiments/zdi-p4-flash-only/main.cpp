/* Console8 stock-MOS write-only recovery, explicitly requested by Author.
 * ZDI/init/flash algorithm: AgonPlatform/agon-recovery 95d68464.
 * P4 GPIO/USB/harness isolation adapted from maintained Extender recovery.
 * No eZ80 reads, identity/CRC gates, dumps, retries or flash-on-boot.
 */
#include <Arduino.h>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <driver/gpio.h>
#include <driver/usb_serial_jtag.h>
#include <cstring>

#include "generated/mos_recovery_payload.hpp"

namespace {

using namespace agon_extender::diagnostic::recovery_payload;

constexpr uint8_t kZdiTckPin = 46;
constexpr uint8_t kZdiTdiPin = 47;
constexpr uint32_t kFlashAgentLoad = 0x040000;
constexpr uint32_t kMosLoad = 0x050000;
constexpr uint32_t kMosSizeAddress = 0x070000;
constexpr size_t kChunkSize = 256; // Yield between short ZDI bursts for IDF idle tasks.

// eZ80F92 I/O addresses copied from the same agon-recovery authority.
constexpr uint8_t kTmr0Ctl = 0x80;
constexpr uint8_t kTmr1Ctl = 0x83;
constexpr uint8_t kTmr2Ctl = 0x86;
constexpr uint8_t kTmr3Ctl = 0x89;
constexpr uint8_t kTmr4Ctl = 0x8C;
constexpr uint8_t kTmr5Ctl = 0x8F;
constexpr uint8_t kPbDdr = 0x9B;
constexpr uint8_t kPbAlt1 = 0x9C;
constexpr uint8_t kPbAlt2 = 0x9D;
constexpr uint8_t kPcDdr = 0x9F;
constexpr uint8_t kPcAlt1 = 0xA0;
constexpr uint8_t kPcAlt2 = 0xA1;
constexpr uint8_t kPdDdr = 0xA3;
constexpr uint8_t kPdAlt1 = 0xA4;
constexpr uint8_t kPdAlt2 = 0xA5;
constexpr uint8_t kCs0Lbr = 0xA8;
constexpr uint8_t kCs0Ubr = 0xA9;
constexpr uint8_t kCs0Ctl = 0xAA;
constexpr uint8_t kCs1Ctl = 0xAD;
constexpr uint8_t kCs2Ctl = 0xB0;
constexpr uint8_t kCs3Ctl = 0xB3;
constexpr uint8_t kRamCtl = 0xB4;
constexpr uint8_t kRamAddrU = 0xB5;
constexpr uint8_t kSpiCtl = 0xBA;
constexpr uint8_t kUart0Ier = 0xC1;
constexpr uint8_t kI2cCtl = 0xCB;
constexpr uint8_t kUart1Ier = 0xD1;
constexpr uint8_t kRtcCtrl = 0xED;
constexpr uint8_t kCs0Bmc = 0xF0;
constexpr uint8_t kFlashAddrU = 0xF7;
constexpr uint8_t kFlashCtrl = 0xF8;
constexpr uint8_t kFlashIrq = 0xFB;

static_assert(kMosSize > 0 && kMosSize <= 131072);
static_assert(kFlashAgentSize == 90);

void report(const char* format, ...) {
  char text[1024];
  va_list arguments;
  va_start(arguments, format);
  int n = vsnprintf(text, sizeof(text), format, arguments);
  va_end(arguments);
  if (n < 0 || n >= static_cast<int>(sizeof(text))) {
    while (true) delay(1000);
  }
  // Own USB Serial/JTAG explicitly; historical stdin/Arduino Serial did not
  // deliver input reliably. A failed output halts progression, never retries erase.
  if (usb_serial_jtag_write_bytes(text, n, pdMS_TO_TICKS(2000)) != n) {
    while (true) delay(1000);
  }
}

class Zdi {
 public:
  enum class Register : uint8_t {
    BreakControl = 0x10,
    WriteDataLow = 0x13,
    ReadWriteControl = 0x16,
    Instruction2 = 0x23,
    Instruction1 = 0x24,
    Instruction0 = 0x25,
    WriteMemory = 0x30,
  };

  enum class CpuRegister : uint8_t {
    AfMb = 0,
    Bc = 1,
    De = 2,
    Hl = 3,
    Ix = 4,
    Iy = 5,
    Sp = 6,
    Pc = 7,
    SetAdl = 8,
  };

  void begin() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    gpio_config_t tck = {
        .pin_bit_mask = 1ULL << kZdiTckPin,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tck);
    gpio_config_t tdi = {
        .pin_bit_mask = 1ULL << kZdiTdiPin,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tdi);
  }

  void writeRegister(Register reg, uint8_t value) {
    writeRegisters(reg, 1, &value);
  }

  void writeRegisters(Register reg, uint8_t count, const uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), false);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      writeByte(*values++);
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void halt() { writeRegister(Register::BreakControl, 0x80); }
  void resume() { writeRegister(Register::BreakControl, 0x00); }

  void writeCpuRegister(CpuRegister reg, uint32_t value) {
    const uint8_t bytes[3] = {
        static_cast<uint8_t>(value),
        static_cast<uint8_t>(value >> 8),
        static_cast<uint8_t>(value >> 16),
    };
    writeRegisters(Register::WriteDataLow, 3, bytes);
    writeRegister(Register::ReadWriteControl,
                  static_cast<uint8_t>(reg) | 0x80);
  }

  void writeMemory(uint32_t address, size_t count, const uint8_t* input) {
    writeCpuRegister(CpuRegister::Pc, address);
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(Register::WriteMemory), false);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      writeByte(*input++);
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeMemory24(uint32_t address, uint32_t value) {
    const uint8_t bytes[3] = {
        static_cast<uint8_t>(value),
        static_cast<uint8_t>(value >> 8),
        static_cast<uint8_t>(value >> 16),
    };
    writeMemory(address, sizeof(bytes), bytes);
  }

  void injectOut(uint8_t port, uint8_t value) {
    writeRegister(Register::Instruction1, value);
    writeRegister(Register::Instruction0, 0x3E);  // LD A,value
    writeRegister(Register::Instruction1, port);
    writeRegister(Register::Instruction0, 0xD3);  // OUT (port),A
  }

  void disableInterrupts() { writeRegister(Register::Instruction0, 0xF3); }

 private:
  void signalStart() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), 1);
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_OUTPUT);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), 0);
    delayMicroseconds(1); // Explicit ZDI start hold on the native build.
  }
  void signalContinue() { writeBit(false); }
  void signalDone() { writeBit(true); }
  void writeBit(bool value) {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 0);
    delayMicroseconds(1); // Allow the external target to respond to the edge.
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), value ? 1 : 0);
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_OUTPUT);
    delayMicroseconds(1); // Data setup before the sampling clock edge.
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    delayMicroseconds(1); // Bound the high phase independently of code speed.
  }
  void addressRegister(uint8_t reg, bool read) {
    for (int bit = 6; bit >= 0; --bit) {
      writeBit((reg & (1U << bit)) != 0);
    }
    writeBit(read);
  }
  void writeByte(uint8_t value) {
    for (int bit = 7; bit >= 0; --bit) {
      writeBit((value & (1U << bit)) != 0);
    }
  }

};

Zdi zdi;

void initializeEz80() {
  zdi.halt();
  zdi.writeRegister(Zdi::Register::ReadWriteControl, 8); // Set ADL: write only.
  zdi.disableInterrupts();
  zdi.injectOut(kSpiCtl, 0x04);
  for (const uint8_t port : {kPbDdr, kPcDdr, kPdDdr}) zdi.injectOut(port, 0xFF);
  for (const uint8_t port : {kPbAlt1, kPcAlt1, kPdAlt1,
                             kPbAlt2, kPcAlt2, kPdAlt2}) zdi.injectOut(port, 0);
  for (const uint8_t port : {kTmr0Ctl, kTmr1Ctl, kTmr2Ctl,
                             kTmr3Ctl, kTmr4Ctl, kTmr5Ctl,
                             kUart0Ier, kUart1Ier, kI2cCtl,
                             kFlashIrq}) zdi.injectOut(port, 0);
  zdi.injectOut(kSpiCtl, 0x04);
  zdi.injectOut(kRtcCtrl, 0);
  zdi.injectOut(kFlashAddrU, 0x00);
  zdi.injectOut(kFlashCtrl, 0x28);
  zdi.injectOut(kRamAddrU, 0xB7);
  zdi.injectOut(kRamCtl, 0x80);
  zdi.injectOut(kCs0Lbr, 0x04);
  zdi.injectOut(kCs0Ubr, 0x0B);
  zdi.injectOut(kCs0Bmc, 0x01);
  zdi.injectOut(kCs0Ctl, 0x08);
  zdi.injectOut(kCs1Ctl, 0x00);
  zdi.injectOut(kCs2Ctl, 0x00);
  zdi.injectOut(kCs3Ctl, 0x00);
  zdi.writeCpuRegister(Zdi::CpuRegister::Sp, 0x0BFFFF);
  zdi.writeCpuRegister(Zdi::CpuRegister::Pc, 0x000000);
}

void upload(uint32_t address, const uint8_t* data, size_t size) {
  size_t done = 0;
  while (done < size) {
    const size_t count = min(kChunkSize, size - done);
    zdi.writeMemory(address + done, count, data + done);
    done += count;
    delay(1);
    if ((done % (16 * kChunkSize)) == 0 || done == size) {
      report("  uploaded %u/%u bytes\n", static_cast<unsigned>(done),
             static_cast<unsigned>(size));
    }
  }
}

// No target access occurs before this exact console command.
void waitForFlash() {
  char line[16] = {};
  size_t used = 0;
  bool overflow = false;
  uint32_t last = millis() - 2000U;
  while (true) {
    if (millis() - last >= 2000U) {
      report("READY P4-FLASH-ONLY r01 GREEN=46 BLUE=47\n");
      last = millis();
    }
    char ch;
    if (usb_serial_jtag_read_bytes(&ch, 1, pdMS_TO_TICKS(20)) != 1) continue;
    if (ch == '\r') continue;
    if (ch == '\n') {
      line[used] = 0;
      if (!overflow && strcmp(line, "FLASH") == 0) return;
      used = 0;
      overflow = false;
    } else if (used + 1 < sizeof(line)) {
      line[used++] = ch;
    } else {
      overflow = true;
    }
  }
}

void releaseZdi() {
  gpio_config_t released = {
      .pin_bit_mask = (1ULL << kZdiTckPin) | (1ULL << kZdiTdiPin),
      .mode = GPIO_MODE_INPUT,
      .pull_up_en = GPIO_PULLUP_DISABLE,
      .pull_down_en = GPIO_PULLDOWN_DISABLE,
      .intr_type = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&released));
}

[[noreturn]] void recover() {
  report("FLASH START stock MOS 3.0.2; all target reads disabled\n");
  zdi.begin();
  initializeEz80();
  report("Uploading stock MOS: %u bytes\n", static_cast<unsigned>(kMosSize));
  upload(kMosLoad, kMosImage, kMosSize);
  zdi.writeMemory24(kMosSizeAddress, kMosSize);
  report("Uploading original 90-byte flash agent\n");
  upload(kFlashAgentLoad, kFlashAgent, kFlashAgentSize);
  report("Executing flash agent; waiting 10 seconds without ZDI access\n");
  zdi.writeCpuRegister(Zdi::CpuRegister::Pc, kFlashAgentLoad);
  zdi.resume();
  for (int second = 1; second <= 10; ++second) {
    delay(1000);
    report("  flash wait %d/10\n", second);
  }
  releaseZdi();
  report("BLIND FLASH SEQUENCE FINISHED - NOT VERIFIED\n");
  report("GREEN and BLUE released. Power-cycle Console8; check MOS banner.\n");
  while (true) delay(1000); // One invocation; never automatic retry.
}

} // namespace

void setup() {
  // All existing Extender harness endpoints remain high impedance, no pulls.
  constexpr uint64_t harness = (1ULL<<9)|(1ULL<<10)|(1ULL<<11)|(1ULL<<12)|
      (1ULL<<13)|(1ULL<<14)|(1ULL<<15)|(1ULL<<17)|(1ULL<<20)|(1ULL<<21)|
      (1ULL<<22)|(1ULL<<23)|(1ULL<<26)|(1ULL<<27)|(1ULL<<32)|(1ULL<<33);
  gpio_config_t released = {.pin_bit_mask=harness, .mode=GPIO_MODE_INPUT,
      .pull_up_en=GPIO_PULLUP_DISABLE, .pull_down_en=GPIO_PULLDOWN_DISABLE,
      .intr_type=GPIO_INTR_DISABLE};
  ESP_ERROR_CHECK(gpio_config(&released));
  releaseZdi();
  if (!usb_serial_jtag_is_driver_installed()) {
    usb_serial_jtag_driver_config_t config = {.tx_buffer_size=4096, .rx_buffer_size=256};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&config));
  }
  delay(1000);
  report("\nP4-FLASH-ONLY r01; stock MOS 3.0.2; GREEN=GPIO46 BLUE=GPIO47\n");
  report("Payload %u bytes SHA256 %s\n", static_cast<unsigned>(kMosSize), kMosSha256);
  report("No target reads. No flash on boot. Exact FLASH command required.\n");
  waitForFlash();
  recover();
}

void loop() { delay(1000); }
