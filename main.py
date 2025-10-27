# main.py
# SED1515 - Laboratoire 5 : I2C, Temps et Journal
# Jeu qui mesure la précision de votre perception du temps (15 secondes)
# Utilise le module RTC DS3231 via I2C et un bouton poussoir

from machine import Pin, I2C
import time, os
from rtc_ds3231 import DS3231

# --- Configuration matérielle ---
I2C_ID = 1
PIN_SDA = 14
PIN_SCL = 15
BUTTON_PIN = 16   # Broche du bouton (actif bas)
LOG_PATH = "log.txt"

# --- Initialisation du bus I2C et du RTC ---
i2c = I2C(I2C_ID, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400000)
rtc = DS3231(i2c)

# --- Initialisation du bouton ---
btn = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

def attendre_appui(message="Appuyez sur le bouton..."):
    """Attend que le bouton soit pressé puis relâché (avec anti-rebond)."""
    print(message)
    # Attendre l’appui
    while btn.value() == 1:
        time.sleep_ms(10)
    # Attendre le relâchement
    while btn.value() == 0:
        time.sleep_ms(10)

def initialiser_log(f):
    """Ajoute un en-tête au fichier log si nécessaire."""
    try:
        taille = os.stat(LOG_PATH)[6]
        if taille == 0:
            f.write("timestamp,temps_ecoule\n")
            f.flush()
    except:
        f.write("timestamp,temps_ecoule\n")
        f.flush()

def mesurer_jeu():
    """Effectue une partie du jeu et retourne le temps écoulé."""
    attendre_appui("Appuyez pour commencer à compter 15 secondes...")
    debut = rtc.seconds_since_midnight()
    attendre_appui("Appuyez de nouveau quand vous pensez que 15 secondes sont passées.")
    fin = rtc.seconds_since_midnight()

    # Gestion du passage de minuit
    if fin < debut:
        fin += 24 * 3600

    ecoule = fin - debut
    return rtc.datetime_string(), ecoule

def main():
    print("=== Jeu des 15 secondes ===")
    print("Adresses I2C détectées :", [hex(a) for a in i2c.scan()])
    print("Heure actuelle du RTC :", rtc.datetime_string())
    print("Appuyez sur Ctrl+C pour arrêter le programme.\n")

    log = open(LOG_PATH, "a")
    try:
        initialiser_log(log)
        while True:
            horodatage, ecoule = mesurer_jeu()
            print(f"Temps mesuré : {ecoule} secondes")
            log.write(f"{horodatage},{ecoule}\n")
            log.flush()
            print("-------------------------------\n")
    except KeyboardInterrupt:
        print("\nArrêt du programme par l'utilisateur.")
    finally:
        log.close()
        print("Fichier journal enregistré :", LOG_PATH)

if __name__ == "__main__":
    main()
