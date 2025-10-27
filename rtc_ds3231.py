# rtc_ds3231.py
# Bibliothèque pour le module d'horloge en temps réel DS3231 (I2C)
# Compatible avec le Raspberry Pi Pico (ou Pico W/WH)

from machine import I2C
import time

# Adresse I2C du DS3231
_DS3231_ADDR = 0x68

# Adresse du premier registre (secondes)
_REG_SECONDS = 0x00

# Conversion entre BCD et entier normal
def _bcd_to_int(b):
    # Convertit une valeur codée BCD (ex: 0x45 → 45)
    return (b >> 4) * 10 + (b & 0x0F)

def _int_to_bcd(v):
    # Convertit un entier (ex: 45 → 0x45)
    return ((v // 10) << 4) | (v % 10)

class DS3231:
    def __init__(self, i2c: I2C, addr: int = _DS3231_ADDR):
        # Initialise la communication I2C avec le module RTC
        self.i2c = i2c
        self.addr = addr

    def read_raw7(self):
        # Lit les 7 premiers registres (secondes, minutes, heures, jour, date, mois, année)
        return self.i2c.readfrom_mem(self.addr, _REG_SECONDS, 7)

    def read_datetime(self):
        """Retourne un dictionnaire contenant l'heure et la date actuelles."""
        b = self.read_raw7()

        sec = _bcd_to_int(b[0] & 0x7F)        # Masque le bit CH
        minute = _bcd_to_int(b[1] & 0x7F)
        hour_raw = b[2]

        # Gère les formats 12h et 24h
        if hour_raw & 0x40:                   # Mode 12h
            hour = _bcd_to_int(hour_raw & 0x1F)
            ampm = (hour_raw & 0x20) >> 5     # 0=AM, 1=PM
            if ampm:
                hour = (hour % 12) + 12
            else:
                hour = hour % 12
        else:
            hour = _bcd_to_int(hour_raw & 0x3F)

        wday = _bcd_to_int(b[3] & 0x07)
        mday = _bcd_to_int(b[4] & 0x3F)
        month = _bcd_to_int(b[5] & 0x1F)
        year = 2000 + _bcd_to_int(b[6])

        return dict(year=year, month=month, mday=mday, wday=wday,
                    hour=hour, minute=minute, second=sec)

    def datetime_string(self):
        """Retourne la date et l’heure sous forme de texte."""
        dt = self.read_datetime()
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            dt["year"], dt["month"], dt["mday"],
            dt["hour"], dt["minute"], dt["second"]
        )

    def seconds_since_midnight(self):
        """Retourne le nombre de secondes écoulées depuis minuit."""
        dt = self.read_datetime()
        return dt["hour"] * 3600 + dt["minute"] * 60 + dt["second"]

    def set_datetime(self, year, month, mday, hour, minute, second, wday=1):
        """Permet de régler l’heure et la date manuellement (optionnel)."""
        payload = bytes((
            _int_to_bcd(second & 0x7F),
            _int_to_bcd(minute & 0x7F),
            _int_to_bcd(hour & 0x3F),
            _int_to_bcd(wday & 0x07),
            _int_to_bcd(mday & 0x3F),
            _int_to_bcd(month & 0x1F),
            _int_to_bcd((year - 2000) & 0xFF),
        ))
        self.i2c.writeto_mem(self.addr, _REG_SECONDS, payload)
        time.sleep_ms(10)
