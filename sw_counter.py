from machine import Pin
from time import sleep

sw1 = Pin(16, Pin.IN, Pin.PULL_UP)
red = Pin(2, Pin.OUT)

count = 0
prev = None

while True:
    current = sw1.value()
    if current == 0 and prev == 1:
        count += 1
        print("Count = ",count)
    prev = current
        
        
    
