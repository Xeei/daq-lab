command check port
```bash
ls /dev/cu.*
```

comomand erase
```bash
esptool --port /dev/cu.usbserial-DA5EOKKX erase-flash
```

command flash
```bash
esptool --baud 460800 write-flash 0x1000 ESP32_GENERIC-20251209-v1.27.0.bin
```