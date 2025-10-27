# i2c_scan.py
# Vérifie la détection des périphériques I2C (ex: DS3231)

from machine import I2C, Pin

# Bus I2C1 : SDA=GP14, SCL=GP15
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)

adresses = i2c.scan()
print("Périphériques I2C détectés :", [hex(a) for a in adresses])
# On devrait voir : 0x68 (RTC) et 0x57 (EEPROM)
