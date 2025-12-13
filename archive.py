#############


dir_path = "K:\ETL\DATA_FICHIERS\honore_gaming\extracted"
import os
from datetime import  datetime


# Lister les fichiers dans le dossier
for filename in os.listdir(dir_path):
    if filename.startswith("dail"):
        try:
            # Enlever l'extension pour extraire la date proprement
            filename_without_ext = os.path.splitext(filename)[0]
            date_str = filename_without_ext.split("_")[-1] # ex: "20250101"
            date_format = "%Y-%m-%d"
            date_format = "%Y%m%d"
            date_obj = datetime.strptime(date_str, date_format )
            date_format_dest = "%d-%m-%Y"
            date_format_dest = "%Y-%m-%d"
            formatted_date = date_obj.strftime(date_format_dest)

            # Récupérer l'extension réelle
            _, ext = os.path.splitext(filename)

            # Nouveau nom

            new_filename = f"honore_gaming_{formatted_date}{ext}"
            new_filename = f"honore_gaming_{formatted_date}{ext}"

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