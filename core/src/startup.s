.syntax unified
.cpu cortex-m3
.fpu softvfp
.thumb

.global g_pfnVectors
.global Reset_Handler

.section .isr_vector, "a", %progbits
g_pfnVectors:
    .word  _estack
    .word  Reset_Handler
    .word  NMI_Handler
    .word  HardFault_Handler
    .word  MemManage_Handler
    .word  BusFault_Handler
    .word  UsageFault_Handler
    .word  0
    .word  0
    .word  0
    .word  0
    .word  SVC_Handler
    .word  DebugMon_Handler
    .word  0
    .word  PendSV_Handler
    .word  SysTick_Handler

.section .text.Default_Handler, "ax", %progbits
Default_Handler:
    b .

.weak NMI_Handler
.thumb_set NMI_Handler, Default_Handler
.weak HardFault_Handler
.thumb_set HardFault_Handler, Default_Handler
.weak MemManage_Handler
.thumb_set MemManage_Handler, Default_Handler
.weak BusFault_Handler
.thumb_set BusFault_Handler, Default_Handler
.weak UsageFault_Handler
.thumb_set UsageFault_Handler, Default_Handler
.weak SVC_Handler
.thumb_set SVC_Handler, Default_Handler
.weak DebugMon_Handler
.thumb_set DebugMon_Handler, Default_Handler
.weak PendSV_Handler
.thumb_set PendSV_Handler, Default_Handler
.weak SysTick_Handler
.thumb_set SysTick_Handler, Default_Handler

.section .text.Reset_Handler, "ax", %progbits
Reset_Handler:
    ldr   r0, =_sdata
    ldr   r1, =_edata
    ldr   r2, =_sidata

1:
    cmp   r0, r1
    it    lt
    ldrlt r3, [r2], #4
    it    lt
    strlt r3, [r0], #4
    blt   1b
    ldr   r0, =_sbss
    ldr   r1, =_ebss

2:
    cmp   r0, r1
    it    lt
    movlt r2, #0
    it    lt
    strlt r2, [r0], #4
    blt   2b
    bl    SystemInit
    bl    main
LoopForever:
    b LoopForever