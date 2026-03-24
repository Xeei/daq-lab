from machine import Pin
from time import sleep

sw2 = Pin(14, Pin.IN, Pin.PULL_UP)
light = Pin(25, Pin.OUT)

count = 0
prev = None

while True:
    current = sw2.value()
    if current == 0 and prev == 1:
        count += 1
        print("Count = ",count)
    prev = current
    
    if count%2 == 0:
        light.value(1)
    else:
        light.value(0)
        
        
    

