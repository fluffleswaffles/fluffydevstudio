#include "fluffy.h"

#define RCC_BASE 0x40021000
#define RCC_APB2ENR (*(volatile uint32_t*)(RCC_BASE + 0x18))

uint32_t millis(void) {
    return systick_count;
}

void delay(uint32_t ms) {
    uint32_t start = millis();
    while ((millis() - start) < ms);
}

void fluffy_init(void) {
    RCC_APB2ENR |= (1 << 2) | (1 << 3);
}

void pinMode(Pin pin, int mode) {
    GPIO_TypeDef* port = (GPIO_TypeDef*)pin.port;
    uint32_t pos = __builtin_ctz(pin.pin);

    volatile uint32_t* reg =
        (pos < 8) ? &port->CRL : &port->CRH;

    uint32_t shift =
        (pos < 8) ? (pos * 4) : ((pos - 8) * 4);

    *reg &= ~(0xF << shift);

    if (mode == OUTPUT) {
        *reg |= (0x1 << shift);
    } else if (mode == INPUT_PULLUP) {
        *reg |= (0x8 << shift);
        port->BSRR = pin.pin;
    }
}

void digitalWrite(Pin pin, int value) {
    GPIO_TypeDef* port = (GPIO_TypeDef*)pin.port;
    if (value)
        port->BSRR = pin.pin;
    else
        port->BRR = pin.pin;
}

int digitalRead(Pin pin) {
    GPIO_TypeDef* port = (GPIO_TypeDef*)pin.port;
    return (port->IDR & pin.pin) ? 1 : 0;
}

uint16_t analogRead(Pin pin) {
    ADC1->SQR3 = pin.adc_channel;
    ADC1->CR2 |= (1 << 0);
    while (!(ADC1->SR & (1 << 1)));
    return (uint16_t)ADC1->DR;
}