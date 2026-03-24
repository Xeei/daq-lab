from machine import Pin, ADC, PWM
from time import sleep

LDR_PIN = 36
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_0DB)
light = PWM(Pin(25, Pin.OUT), freq=5000)



while True:
    curr = ldr.read()
    print(curr)
    duty_value = int(curr * (1023 / 4095)*1.5)
    print(duty_value)
    if duty_value < 0: duty_value = 0
    if duty_value > 1023: duty_value = 1023
    light.duty(duty_value)
    sleep(0.1)
    