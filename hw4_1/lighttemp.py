import machine
import time
import math

I2C_ADDR_LM73 = 0x4D
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
adc = machine.ADC(machine.Pin(36))
adc.atten(machine.ADC.ATTN_11DB) # Full range: 3.3V

R1, Lux1 = 1000, 100
R2, Lux2 = 10000, 10
R_FIXED = 10000

m = (math.log10(Lux2) - math.log10(Lux1)) / (math.log10(R2) - math.log10(R1))
b = math.log10(Lux1) - m * math.log10(R1)

def setup_lm73():
    try:
        i2c.writeto_mem(I2C_ADDR_LM73, 0x04, b'\x60')
    except Exception as e:
        print("LM73 Setup Error:", e)

def get_temp():
    raw = i2c.readfrom_mem(I2C_ADDR_LM73, 0x00, 2)
    value = (raw[0] << 8) | raw[1]
    
    if value & 0x8000:
        value -= 65536

    return value / 128.0

def get_lux():
    val = adc.read()
    if val == 0: return 0.0
    r_ldr = ((4095 - val) * R_FIXED) / val
    
    log_lux = m * math.log10(r_ldr) + b
    return 10**log_lux

setup_lm73()

while True:
    temp_c = get_temp()
    lux_val = get_lux()

    print("Light: {:.2f} Lux | Temp: {:.4f} C".format(lux_val, temp_c))
    
    time.sleep(2)
