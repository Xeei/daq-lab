import _thread
from machine import Pin
import network
import time
from umqtt.robust import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS
)


lamp = Pin(25, Pin.OUT)
lamp.value(1)  # turn it off

sw1 = Pin(16, Pin.IN, Pin.PULL_UP)

led_wifi = Pin(2, Pin.OUT)
led_wifi.value(1)  # turn the red led off
led_iot = Pin(12, Pin.OUT)
led_iot.value(1)   # turn the green led off


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
led_wifi.value(0)  # turn the red led on


mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)
mqtt.connect()
led_iot.value(0)   # turn the green led on


lamp = Pin(25, Pin.OUT)
lamp.value(1)  # turn USB lamp off initially
        
def listen_mqtt(topic, payload):
    if topic.decode() == "b6710545849/lamp/sw":
        try:
            value = int(payload)
            print('Receive', value)
            if value == 1:
                lamp.value(0)
            elif value == 0:
                lamp.value(1)
        except ValueError:
            pass
        
def listen_sw(params=None):
    print('Start thread listen switch')
    while True:
        # wait until S1 is pressed
        while sw1.value() == 1:
            pass
        
        # toggle lamp
        lamp.value(1 - lamp.value())
        
        time.sleep(0.01) # debounce
        
        # wait until S1 is released
        while sw1.value() == 0:
            pass
        time.sleep(0.01) # debounce
        
mqtt.set_callback(listen_mqtt)
mqtt.subscribe("b6710545849/lamp/sw")

_thread.start_new_thread(listen_mqtt, ())
_thread.start_new_thread(listen_sw, ())

while True:
    mqtt.check_msg()
