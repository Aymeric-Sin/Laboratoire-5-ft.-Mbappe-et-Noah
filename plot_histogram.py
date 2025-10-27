# plot_histogram.py
# Lit le fichier log.txt et trace un histogramme des temps mesurés

import csv
import matplotlib.pyplot as plt

# Nom du fichier log (copié depuis la Pico)
FICHIER_LOG = "log.txt"

temps = []

# Lecture du fichier log
with open(FICHIER_LOG, "r", encoding="utf-8") as f:
    lecteur = csv.reader(f)
    next(lecteur)  # ignore la première ligne (en-tête)
    for ligne in lecteur:
        if len(ligne) < 2:
            continue
        try:
            temps.append(float(ligne[1]))
        except ValueError:
            pass

# Vérifie qu'on a des données
if not temps:
    print("Aucune donnée trouvée dans le log.")
else:
    plt.hist(temps, bins=range(int(min(temps)) - 1, int(max(temps)) + 2))
    plt.xlabel("Temps mesuré (secondes)")
    plt.ylabel("Nombre d'occurrences")
    plt.title("Jeu des 15 secondes – Histogramme des résultats")
    plt.tight_layout()
    plt.savefig("histogramme.png")
    print("Histogramme sauvegardé sous 'histogramme.png'")
