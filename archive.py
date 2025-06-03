#############
dir_path = "K:\DATA_FICHIERS\BWINNERS"
import os
from datetime import  datetime


# Lister les fichiers dans le dossier
for filename in os.listdir(dir_path):
    if filename.startswith(""):
        try:
            # Enlever l'extension pour extraire la date proprement
            filename_without_ext = os.path.splitext(filename)[0]
            date_str = filename_without_ext.split("_")[-1]  # ex: "20250101"
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")

            # Récupérer l'extension réelle
            _, ext = os.path.splitext(filename)

            # Nouveau nom
            new_filename = f"Bwinner_{formatted_date}_{formatted_date}{ext}"

            # Chemins complets
            old_path = os.path.join(dir_path, filename)
            new_path = os.path.join(dir_path, new_filename)

            # Renommer le fichier
            os.rename(old_path, new_path)
            print(f"✅ Renommé : {filename} → {new_filename}")

            # Appel de la fonction de transformation (à décommenter si tu veux l’utiliser)
            # run_honore_gaming_transformer()

        except Exception as e:
            print(f"❌ Erreur avec le fichier {filename} : {e}")

########"####