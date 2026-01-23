#pragma once
#include <stdint.h>

#define GPIOA_BASE 0x40010800
#define GPIOB_BASE 0x40010C00

typedef struct {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
} GPIO_TypeDef;

#define GPIOA ((GPIO_TypeDef*)GPIOA_BASE)
#define GPIOB ((GPIO_TypeDef*)GPIOB_BASE)

#define GPIO_PIN_0   ((uint16_t)0x0001)
#define GPIO_PIN_1   ((uint16_t)0x0002)
#define GPIO_PIN_2   ((uint16_t)0x0004)
#define GPIO_PIN_3   ((uint16_t)0x0008)
#define GPIO_PIN_4   ((uint16_t)0x0010)
#define GPIO_PIN_5   ((uint16_t)0x0020)
#define GPIO_PIN_6   ((uint16_t)0x0040)
#define GPIO_PIN_7   ((uint16_t)0x0080)

typedef struct {
    GPIO_TypeDef* port;
    uint16_t pin;
    uint8_t adc_channel;
} Pin;

#define INPUT         0
#define OUTPUT        1
#define INPUT_PULLUP 2

#define LOW   0
#define HIGH  1

void pinMode(Pin pin, int mode);
void digitalWrite(Pin pin, int value);
int  digitalRead(Pin pin);

uint32_t millis(void);
void delay(uint32_t ms);

uint16_t analogRead(Pin pin);

#define PA0  ((Pin){GPIOA, GPIO_PIN_0, 0})
#define PA1  ((Pin){GPIOA, GPIO_PIN_1, 1})
#define PA2  ((Pin){GPIOA, GPIO_PIN_2, 2})
#define PA3  ((Pin){GPIOA, GPIO_PIN_3, 3})
#define PA4  ((Pin){GPIOA, GPIO_PIN_4, 4})
#define PA5  ((Pin){GPIOA, GPIO_PIN_5, 5})
#define PA6  ((Pin){GPIOA, GPIO_PIN_6, 6})
#define PA7  ((Pin){GPIOA, GPIO_PIN_7, 7})

#define PB0  ((Pin){GPIOB, GPIO_PIN_0, 8})
#define PB1  ((Pin){GPIOB, GPIO_PIN_1, 9})
#define PB2  ((Pin){GPIOB, GPIO_PIN_2, 10})
#define PB3  ((Pin){GPIOB, GPIO_PIN_3, 11})
#define PB4  ((Pin){GPIOB, GPIO_PIN_4, 12})
#define PB5  ((Pin){GPIOB, GPIO_PIN_5, 13})
#define PB6  ((Pin){GPIOB, GPIO_PIN_6, 14})
#define PB7  ((Pin){GPIOB, GPIO_PIN_7, 15})

extern volatile uint32_t systick_count;

#define ADC1_BASE 0x40012400

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMPR1;
    volatile uint32_t SMPR2;
    volatile uint32_t JOFR1;
    volatile uint32_t JOFR2;
    volatile uint32_t JOFR3;
    volatile uint32_t JOFR4;
    volatile uint32_t HTR;
    volatile uint32_t LTR;
    volatile uint32_t SQR1;
    volatile uint32_t SQR2;
    volatile uint32_t SQR3;
    volatile uint32_t JSQR;
    volatile uint32_t JDR1;
    volatile uint32_t JDR2;
    volatile uint32_t JDR3;
    volatile uint32_t JDR4;
    volatile uint32_t DR;
} ADC_TypeDef;

#define ADC1 ((ADC_TypeDef*)ADC1_BASE)
