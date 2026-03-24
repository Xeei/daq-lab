import _thread
from machine import Pin, Timer
import network
import time
from umqtt.robust import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS
)

TOPIC = "b6710545849/practice/blink"
TOPIC_COUNT = "b6710545849/practice/count"

sw2 = Pin(14, Pin.IN, Pin.PULL_UP)

led_red = Pin(2, Pin.OUT)
led_red.value(1) # turn the red led off

led_green = Pin(12, Pin.OUT)
led_green.value(1)   # turn the green led off

# Start connect wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
print("WLAN Connected")

# Start connect MQTT
mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)
mqtt.connect()
print("MQTT Connected")

# Heart beat use Multi THread
def task_1():
    while True:
        led_green.value(0)
        time.sleep(300)
        led_green.value(1)
        time.sleep(1200)
        

        
is_blink = False
def listen_mqtt(topic, payload):
    global is_blink
    if is_blink:
        print("Led is busy ignore request...")
        return
    if topic.decode() == TOPIC:
        try:
            
            value = int(payload)
            print('Receive', value)
            if (value >= 1 and value <= 5):
                is_blink = True
                for i in range(value):
                    led_green.value(0)
                    time.sleep(0.1)
                    led_green.value(1)
                    time.sleep(0.9)
                is_blink = False
#             if value == 1:
#                 lamp.value(0)
#             elif value == 0:
#                 lamp.value(1)
        except ValueError:
            pass
        
        
        

def listen_sw2():
    sw_couter = 0
    print('Start thread listen switch')
    while True:
        # 1. Wait for the button to be pressed (value goes to 0)
        if sw2.value() == 0: 
            sw_couter += 1
            print("Button Pressed! Sending:", sw_couter)
            
            try:
                # Convert to string and publish
                mqtt.publish(TOPIC_COUNT, str(sw_couter))
            except Exception as e:
                print("Publish failed:", e)
            
            # 2. Debounce/Wait: Stay here until the user lets go of the button
            # This prevents sending 1000 messages in one click
            while sw2.value() == 0:
                time.sleep(0.1)
        
        time.sleep(0.01) # Tiny sleep to let the CPU breathe
        
mqtt.set_callback(listen_mqtt)
mqtt.subscribe(TOPIC)

# _thread.start_new_thread(listen_mqtt, ())
_thread.start_new_thread(listen_sw2, ())

_thread.start_new_thread(task_1, ())

while True:
    mqtt.check_msg()
