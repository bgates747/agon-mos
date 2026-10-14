NAME = menu
RAM_START = 0x90000
RAM_SIZE = 0x18000
LDHAS_ARG_PROCESSING = 0
LDHAS_EXIT_HANDLER = 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS += -std=c11 -Wall -Wextra -Werror
CFLAGS += -I../../build/uart0-suite
obj/main.o: ../../build/uart0-suite/identity.h
