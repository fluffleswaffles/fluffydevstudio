#include "fluffy.h"

uint32_t millis(void) {
    return systick_count;
}

void delay(uint32_t ms) {
    uint32_t start = millis();
    while ((millis() - start) < ms);
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