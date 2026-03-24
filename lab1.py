from time import sleep
from machine import Pin


led = Pin(12, Pin.OUT)
while True:
    print("Turning LED on for 0.1 seconds...")
    led.value(0)
    sleep(0.1)
    print("Turning LED off...")
    led.value(1)
    sleep(0.9)
