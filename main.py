# main.py
# SED1515 - Laboratoire 5 : I2C, Temps et Journal
# Jeu qui mesure la précision de votre perception du temps (15 secondes)
# Utilise le module RTC DS3231 via I2C et un bouton poussoir

from machine import Pin, I2C
import time, os

#  Classe de gestion du module RTC DS3231 
class DS3231:
    def __init__(self, i2c, addr=0x68):
        # Initialise la communication I2C avec l’adresse par défaut du DS3231 (0x68)
        self.i2c, self.addr = i2c, addr

    def _bcd(self, x, rev=False):
        
        # Conversion BCD (Binary Coded Decimal)
        
        # rev=False : transforme une valeur décimale en BCD
        
        # rev=True  : transforme une valeur BCD lue depuis le RTC en décimal
        
        return (x//10<<4 | x%10) if not rev else (x>>4)*10 + (x & 0x0F)

    def get(self):
        
        # Lit les 7 registres de temps du DS3231 (secondes → année)
        
        d = self.i2c.readfrom_mem(self.addr, 0, 7)
        
        # Conversion des 3 premiers octets (secondes, minutes, heures) depuis le format BCD
        
        s, m, h = [self._bcd(x, 1) for x in d[:3]]
        # Conversion de la date (jour, mois, année)
        Y, M, D = 2000+self._bcd(d[6], 1), self._bcd(d[5]&0x1F, 1), self._bcd(d[4], 1)
        return Y, M, D, h, m, s

    def now(self):
        # Renvoie la date et l’heure actuelles sous forme de chaîne formatée
        Y, M, D, h, m, s = self.get()
        return f"{Y:04}-{M:02}-{D:02} {h:02}:{m:02}:{s:02}"

    def sec_midnight(self):
        # Calcule le nombre de secondes écoulées depuis minuit
        _, _, _, h, m, s = self.get()
        return h*3600 + m*60 + s


# Configuration matérielle 
i2c = I2C(1, sda=Pin(14), scl=Pin(15))   # Bus I2C utilisé (canal 1, broches 14 et 15)

rtc = DS3231(i2c)                        # Création d’un objet DS3231 pour accéder au RTC

btn = Pin(22, Pin.IN, Pin.PULL_DOWN)     # Bouton poussoir relié à la broche GPIO 22

LOG = "log.txt"                          # Nom du fichier journal

def wait_press(msg="Appuyez..."):
    
    """Attend une pression et un relâchement du bouton (anti-rebond simple)."""
    print(msg)
    
    while btn.value(): time.sleep_ms(10)     # Attente de l’appui
        
    while not btn.value(): time.sleep_ms(10) # Attente du relâchement

def init_log(f):
    """Crée le fichier log avec un en-tête s’il n’existe pas encore."""
    
    if not LOG in os.listdir() or os.stat(LOG)[6]==0:
        
        f.write("timestamp,temps_ecoule\n")

def play():
    """Lance une partie du jeu des 15 secondes et retourne le temps écoulé."""
    
    wait_press("Appuyez pour démarrer (15s)...")
    
    t0 = rtc.sec_midnight()        # Heure de départ (en secondes depuis minuit) 
    
    wait_press("Appuyez quand terminé.")
    t1 = rtc.sec_midnight()                 # Heure d’arrêt
    
    if t1 < t0: t1 += 86400                # Gestion du passage à minuit (ajoute 24h en secondes)
        
    return rtc.now(), t1 - t0            # Retourne (horodatage, durée)

# Programme principal 

print("=== Jeu des 15 secondes ===")

print("I2C détecté :", [hex(a) for a in i2c.scan()])   # Vérifie la présence du module RTC

print("Heure RTC :", rtc.now())

with open(LOG, "a") as f:
    
    init_log(f)
    
    try:
        while True:
            ts, d = play() 
            
            print(f"→ {d}s\n")           # Affiche la durée sur la console
            
            f.write(f"{ts},{d}\n")       # Sauvegarde dans le fichier log
            
            f.flush()
            
    except KeyboardInterrupt:
        
        # Interruption par l’utilisateur (Ctrl+C)
        
        print("Arrêt, log sauvegardé :", LOG)

