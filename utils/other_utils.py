import os
import fnmatch
import pandas as pd
from dotenv import load_dotenv
import shutil

def move_file(source_file, dest_path, dest_file, logger = None):
    if os.path.exists(dest_file):
        if logger:
            logger.info(f"Suppression du fichier existant : {dest_file}")
        os.remove(dest_file)
    shutil.move(source_file, dest_path)

def load_env():
    load_dotenv("./.env")

from utils.date_utils import sleep
import time

def loading(text, delay=.5, duration=10, show_countdown=False):
    """
    Affiche un texte avec un effet de chargement (points animés) pendant une durée donnée.

    :param text: Le texte à afficher avant les points de chargement.
    :param delay: Le délai entre chaque mise à jour des points (en secondes).
    :param duration: La durée totale du chargement (en secondes).
    """
    print(end=text, flush=True)
    n_dots = 0
    start_time = time.time()  # Enregistre le temps de début

    while True:
        # if show_countdown:
        #     print(end=f"{int(duration - time.time() + start_time)}", flush=True)
        # Vérifie si la durée totale a été atteinte
        if time.time() - start_time >= duration:
            break

        if n_dots == 3:
            # Efface les trois points précédents
            print(end='\b\b\b', flush=True)
            print(end='   ', flush=True)
            print(end='\b\b\b', flush=True)
            n_dots = 0
        else:
            # Ajoute un point supplémentaire
            print(end='.', flush=True)
            n_dots += 1

        sleep(delay)

    # Efface complètement le texte et les points à la fin
    print(end='\b' * (len(text) + 3), flush=True)
    print(end=' ' * (len(text) + 3), flush=True)
    print(end='\b' * (len(text) + 3), flush=True)

# Exemple d'utilisation
