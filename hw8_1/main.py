import _thread
import time
import math
import network
from machine import Pin, I2C, ADC, WDT
import ujson
from umqtt.robust import MQTTClient
from config import WIFI_SSID, WIFI_PASS, MQTT_BROKER, MQTT_USER, MQTT_PASS

# ── Pin setup ────────────────────────────────────────────────
led_green = Pin(12, Pin.OUT); led_green.value(1)
i2c       = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
adc       = ADC(Pin(36)); adc.atten(ADC.ATTN_11DB)

# ── LDR calibration constants ─────────────────────────────────
R_FIXED = 10000
R1, Lux1 = 1000, 100
R2, Lux2 = 10000, 10
m = (math.log10(Lux2) - math.log10(Lux1)) / (math.log10(R2) - math.log10(R1))
b = math.log10(Lux1) - m * math.log10(R1)

# ── Fixed location ────────────────────────────────────────────
LATITUDE  = 13.7270
LONGITUDE = 100.5247

# ── Config ────────────────────────────────────────────────────
TOPIC            = "b6710545849/sensors"
PUBLISH_INTERVAL = 600  # 10 minutes

mqtt_lock = _thread.allocate_lock()
mqtt      = None

# ── WiFi ──────────────────────────────────────────────────────
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    if not wlan.isconnected():
        raise RuntimeError("WiFi failed")
    print("WiFi connected:", wlan.ifconfig())

# ── MQTT ──────────────────────────────────────────────────────
def connect_mqtt():
    client = MQTTClient(client_id="", server=MQTT_BROKER,
                        user=MQTT_USER, password=MQTT_PASS)
    client.connect()
    print("MQTT connected")
    return client

# ── Sensors ───────────────────────────────────────────────────
def read_temperature():
    try:
        i2c.writeto_mem(0x4D, 0x04, b'\x60')  # configure LM73
    except Exception as e:
        print("LM73 setup error:", e)
    raw = i2c.readfrom_mem(0x4D, 0x00, 2)
    value = (raw[0] << 8) | raw[1]
    if value & 0x8000:
        value -= 65536
    return round(value / 128.0, 2)

def read_lux():
    uv = adc.read_uv()          # microvolts, more accurate than read()
    if uv == 0:
        return 0.0
    v = uv / 1_000_000          # convert to volts
    r_ldr = R_FIXED * v / (3.3 - v)   # slide 27 formula exactly
    if r_ldr <= 0:
        return 0.0
    log_lux = m * math.log10(r_ldr) + b
    return round(10 ** log_lux, 2)

# ── Task 1: Heartbeat ─────────────────────────────────────────
def task_heartbeat():
    while True:
        led_green.value(0); time.sleep(0.3)
        led_green.value(1); time.sleep(1.2)

# ── Task 2: Publish sensors as JSON ──────────────────────────
def task_publish_sensors():
    global mqtt
    while True:
        try:
            payload = ujson.dumps({
                "temperature": read_temperature(),
                "light":       read_lux(),
                "latitude":    LATITUDE,
                "longitude":   LONGITUDE
            })
            with mqtt_lock:
                mqtt.publish(TOPIC, payload)
            print("Published:", payload)
        except Exception as e:
            print("Publish error:", e)
            try:
                with mqtt_lock:
                    mqtt = connect_mqtt()
            except Exception as e2:
                print("Reconnect failed:", e2)
        time.sleep(PUBLISH_INTERVAL)

# ── Main ──────────────────────────────────────────────────────
def main():
    global mqtt
    time.sleep(3)
    while True:
        try:
            connect_wifi()
            mqtt = connect_mqtt()
            break
        except Exception as e:
            print("Startup failed, retrying in 10s:", e)
            time.sleep(10)

    wdt = WDT(timeout=60000)
    _thread.start_new_thread(task_heartbeat, ())
    _thread.start_new_thread(task_publish_sensors, ())

    while True:
        wdt.feed()
        time.sleep(5)

main()