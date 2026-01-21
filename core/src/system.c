#include <stdint.h>

uint32_t SystemCoreClock = 72000000;
volatile uint32_t systick_count = 0;

void SystemCoreClockUpdate(void)
{
    SystemCoreClock = 72000000;
}

#define RCC_BASE      0x40021000
#define FLASH_BASE    0x40022000

#define RCC_CR        (*(volatile uint32_t*)(RCC_BASE + 0x00))
#define RCC_CFGR      (*(volatile uint32_t*)(RCC_BASE + 0x04))
#define FLASH_ACR     (*(volatile uint32_t*)(FLASH_BASE + 0x00))

void SystemInit(void)
{
    RCC_CR |= (1 << 16);
    while (!(RCC_CR & (1 << 17)));
    FLASH_ACR |= 0x02;
    RCC_CFGR &= ~(0xF << 18);
    RCC_CFGR |=  (7 << 18);
    RCC_CFGR |=  (1 << 16);
    RCC_CR |= (1 << 24);
    while (!(RCC_CR & (1 << 25)));
    RCC_CFGR &= ~(0x3 << 0);
    RCC_CFGR |=  (0x2 << 0);
    while (((RCC_CFGR >> 2) & 0x3) != 0x2);

    SystemCoreClockUpdate();
}

void SysTick_Handler(void) {
    systick_count++;
}