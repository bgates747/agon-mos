/* Identity-only P4 ZDI reader. No MOS/agent payload, flash command,
 * CPU register writes, halt, RAM access or recovery path exists in this build.
 * Read transaction timing matches the preceding P4 checked r01 image.
 */
#include <Arduino.h>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <driver/gpio.h>
#include <driver/usb_serial_jtag.h>
namespace {
constexpr uint8_t kZdiTckPin=46;
constexpr uint8_t kZdiTdiPin=47;
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
    IdLow = 0x00,
    IdRevision = 0x02,
    Status = 0x03,
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

  uint8_t readRegister(Register reg) {
    uint8_t value = 0;
    readRegisters(reg, 1, &value);
    return value;
  }

  void readRegisters(Register reg, uint8_t count, uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), true);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      *values++ = readByte();
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  uint16_t productId() {
    uint8_t bytes[2] = {};
    readRegisters(Register::IdLow, 2, bytes);
    return static_cast<uint16_t>(bytes[0]) |
           (static_cast<uint16_t>(bytes[1]) << 8);
  }

  uint8_t revision() { return readRegister(Register::IdRevision); }
  uint8_t status() { return readRegister(Register::Status); }
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
  bool readBit() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 0);
    delayMicroseconds(1); // Allow the external target to respond to the edge.
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_INPUT);
    delayMicroseconds(1);
    const bool value =
        gpio_get_level(static_cast<gpio_num_t>(kZdiTdiPin)) != 0;
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    delayMicroseconds(1);
    return value;
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
  uint8_t readByte() {
    uint8_t value = 0;
    for (int bit = 7; bit >= 0; --bit) {
      value = static_cast<uint8_t>((value << 1) | (readBit() ? 1U : 0U));
    }
    return value;
  }
};

Zdi zdi;
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


void identify() {
  zdi.begin();
  for (unsigned i=1; i<=3; ++i) {
    const uint16_t product=zdi.productId();
    const uint8_t revision=zdi.revision();
    const uint8_t status=zdi.status();
    report("IDENTITY %u product=%04X revision=%02X status=%02X\n",
           i,product,revision,status);
    delay(100);
  }
  releaseZdi();
  report("IDENTITY-ONLY DONE; GREEN and BLUE released; MOS untouched\n");
}
} // namespace
void setup() {
  constexpr uint64_t harness=(1ULL<<9)|(1ULL<<10)|(1ULL<<11)|(1ULL<<12)|
      (1ULL<<13)|(1ULL<<14)|(1ULL<<15)|(1ULL<<17)|(1ULL<<20)|(1ULL<<21)|
      (1ULL<<22)|(1ULL<<23)|(1ULL<<26)|(1ULL<<27)|(1ULL<<32)|(1ULL<<33);
  gpio_config_t pins={.pin_bit_mask=harness,.mode=GPIO_MODE_INPUT,
      .pull_up_en=GPIO_PULLUP_DISABLE,.pull_down_en=GPIO_PULLDOWN_DISABLE,
      .intr_type=GPIO_INTR_DISABLE};
  ESP_ERROR_CHECK(gpio_config(&pins));
  releaseZdi();
  if (!usb_serial_jtag_is_driver_installed()) {
    usb_serial_jtag_driver_config_t config={.tx_buffer_size=4096,.rx_buffer_size=256};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&config));
  }
  delay(1000);
  report("\nP4-IDENTITY-ONLY r01 GREEN=46 BLUE=47; no MOS flash capability\n");
}
void loop() {
  static char line[24]={};
  static size_t used=0;
  static bool overflow=false;
  static uint32_t last=0;
  if (millis()-last>=2000) {
    report("READY P4-IDENTITY-ONLY r01 GREEN=46 BLUE=47\n");
    last=millis();
  }
  char c;
  if (usb_serial_jtag_read_bytes(&c,1,pdMS_TO_TICKS(20))!=1)return;
  if(c=='\r')return;
  if(c=='\n') {
    line[used]=0;
    if(!overflow && strcmp(line,"IDENTIFY")==0) identify();
    else report("COMMAND REFUSED: only IDENTIFY exists\n");
    used=0;overflow=false;
  } else if(used+1<sizeof(line))line[used++]=c;
  else overflow=true;
}
