import _thread
import time
from machine import Pin
led_red = Pin(2, Pin.OUT)
led_green = Pin(12, Pin.OUT)
sw1 = Pin(16, Pin.IN, Pin.PULL_UP)

def task1():
    while True:
        led_red.value(0)
        time.sleep_ms(100)
        led_red.value(1)
        time.sleep_ms(1900)

def task2():
    led_green.value(1)
    while True:
        # wait until S1 is pressed
        while sw1.value() == 1:
            pass
        
        # toggle LED
        led_green.value(1 - led_green.value())
        
        time.sleep(0.01) # debounce
        
        # wait until S1 is released
        while sw1.value() == 0:
            pass
        time.sleep(0.01) # debounce

# create and run threads
_thread.start_new_thread(task1, ())
_thread.start_new_thread(task2, ())

#while True:
#    time.sleep(1)