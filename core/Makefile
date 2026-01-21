MCU      = cortex-m3
CPU      = -mcpu=$(MCU) -mthumb
TARGET   = {{PROJECT_NAME}}

SRC_DIR  = src

C_SRCS   := $(wildcard $(SRC_DIR)/*.c)
S_SRCS   := $(wildcard $(SRC_DIR)/*.s)
ALL_SRCS := $(C_SRCS) $(S_SRCS)

CFLAGS   = $(CPU) -O2 -Wall -ffreestanding -nostdlib -nostartfiles -I$(SRC_DIR) -g
ASFLAGS  = $(CPU)
LDFLAGS  = -T $(SRC_DIR)/linker.ld -Wl,--gc-sections $(CPU) -Wl,-Map=build/$(TARGET).map

all: build/$(TARGET).bin

build/$(TARGET).elf: $(ALL_SRCS)
	@mkdir -p build
	arm-none-eabi-gcc $(C_SRCS) $(ASFLAGS) $(S_SRCS) $(CFLAGS) $(LDFLAGS) -o $@

build/$(TARGET).bin: build/$(TARGET).elf
	arm-none-eabi-objcopy -O binary $< $@
	@echo "Build complete: $@"
	arm-none-eabi-size $<

flash: build/$(TARGET).bin
	st-flash write $< 0x8000000

clean:
	@rm -rf build

.PHONY: all flash clean
