from machine import Pin
import time
led_red = Pin(2, Pin.OUT)
led_green = Pin(12, Pin.OUT)
sw1 = Pin(16, Pin.IN, Pin.PULL_UP)

def task1():
    global timestamp1, task1_state
    if task1_state == 'led-on':
        now = time.ticks_ms()
        if now - timestamp1 >= 100:
            led_red.value(0)
            task1_state = 'led-off'
            timestamp1 = now
    elif task1_state == 'led-off':
        now = time.ticks_ms()
        if now - timestamp1 >= 1900:
            led_red.value(1)
            task1_state = 'led-on'
            timestamp1 = now
    
task1_state = 'led-on'
timestamp1 = time.ticks_ms()
led_red.value(0)

def task2():
    global timestamp2, task2_state
    if task2_state == 'wait-sw-press':
        if sw1.value() == 0: # S1 is pressed
            task2_state = 'debounce1'
            led_green.value(1 - led_green.value())
            timestamp2 = time.ticks_ms()
    elif task2_state == 'debounce1':
        now = time.ticks_ms()
        if now - timestamp2 >= 10:
            task2_state = 'wait-sw-release'
            timestamp2 = now
    elif task2_state == 'wait-sw-release':
        if sw1.value() == 1: # S1 is released
            task2_state = 'debounce2'
            timestamp2 = time.ticks_ms()
    elif task2_state == 'debounce2':
        now = time.ticks_ms()
        if now - timestamp2 >= 10:
            task2_state = 'wait-sw-press'
            timestamp2 = now

task2_state = 'wait-sw-press'
timestamp2 = time.ticks_ms()
led_green.value(1)
while True:
    task1()
    task2()
