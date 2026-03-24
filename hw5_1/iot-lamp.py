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


def sub_callback(topic, payload):
    # use decode instead of direct byte-array comparison
    if topic.decode() == "b6710545849/room603/light/lamp":
        try:
            value = int(payload)
            if value > 10:
                print("Out of Range")
            elif value < 1:
                print("Out of Range")
            else:
                print("In case: ", value)
                for i in range(value):
                    lamp.value(0)
                    time.sleep(1)
                lamp.value(1)
            
        except ValueError:
            pass
    
mqtt.set_callback(sub_callback)
mqtt.subscribe("b6710545849/room603/light/lamp")


while True:
    mqtt.check_msg()