from machine import Pin, Timer
import time
led_red = Pin(2, Pin.OUT)
led_green = Pin(12, Pin.OUT)
sw1 = Pin(16, Pin.IN, Pin.PULL_UP)
task1_timer = Timer(0)
task2_timer = Timer(1)


def task1_start():
    task1_led_on()
    
def task1_led_on(param=None):
    led_red.value(0) # turn LED on
    task1_timer.init(period=100,
    mode=Timer.ONE_SHOT,
    callback=task1_led_off)

def task1_led_off(param=None):
    led_red.value(1) # turn LED off
    task1_timer.init(period=1900,
    mode=Timer.ONE_SHOT,
    callback=task1_led_on)


def task2_start():
    led_green.value(1)
    task2_wait_sw_press()
    
def task2_wait_sw_press(param=None):
    sw1.irq(trigger=Pin.IRQ_FALLING,
    handler=task2_debounce1)
    
def task2_debounce1(param=None):
    led_green.value(1-led_green.value())
    sw1.irq(handler=None)
    task2_timer.init(period=10,
    mode=Timer.ONE_SHOT,
    callback=task2_wait_sw_release)

def task2_wait_sw_release(param=None):
    sw1.irq(trigger=Pin.IRQ_RISING,
    handler=task2_debounce2)
    
def task2_debounce2(param=None):
    sw1.irq(handler=None)
    task2_timer.init(period=10,
    mode=Timer.ONE_SHOT,

    callback=task2_wait_sw_press)

task1_start()
task2_start()

#while True:
#    time.sleep(1)