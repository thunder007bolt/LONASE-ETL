import os
import re
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime
from base.tranformer import  Transformer
from utils.file_manipulation import move_file, check_file_not_empty
import zipfile
import csv


class GitechPhysiqueTransformer(Transformer):
    def __init__(self):
        super().__init__('gitech_physique', 'logs/transformer_gitech_physique.log')
        self.zip_path = self.source_path.parent / "zip"
        self.unused_files_path = self.source_path.parent / "unused_files"
        self.others_files_path = self.source_path.parent / "others"

    def _transform_file(self, file: Path, date=None):
        # categorie = file.name.split("_")[-1].replace('.csv', '')
        # data = pd.read_csv(file, encoding='latin-1', skiprows=1, index_col=False, sep=',')

        """
              Transforme le fichier CSV en gérant la colonne GameName avec des virgules.
        """
        categorie = file.name.split("_")[-1].replace('.csv', '')

        data_rows = []
        headers = []

        try:
            with open(file, 'r', encoding='latin-1', newline='') as f:
                # Gérer la ligne d'en-tête (équivalent à skiprows=1)
                # Lire la première ligne, qui doit être ignorée si elle est un en-tête non désiré
                first_line = f.readline().strip()

                # Lire la ligne des vrais en-têtes
                header_line = f.readline().strip()
                # Nettoyer les en-têtes, en enlevant les espaces si besoin
                headers = [h.strip() for h in header_line.split(',')]

                # Vérifier si 'GameName' est dans les en-têtes
                if 'GameName' not in headers:
                    print(
                        f"Avertissement: La colonne 'GameName' n'a pas été trouvée dans les en-têtes du fichier {file.name}.")
                    print(
                        "Tentative de lecture avec pd.read_csv standard (peut échouer si des virgules sont mal gérées).")
                    # Fallback si GameName n'est pas trouvé ou si le format est inattendu
                    data = pd.read_csv(file, encoding='latin-1', skiprows=1, index_col=False, sep=',')
                    # On continue avec le DataFrame tel que lu par pandas. La logique de GameName ne s'appliquera pas.
                else:
                    game_name_index = headers.index('GameName')

                    # Utiliser csv.reader pour une gestion robuste des guillemets
                    reader = csv.reader(f)

                    for i, row in enumerate(reader):
                        if not row:  # Ignorer les lignes vides potentielles
                            continue

                        processed_row = []

                        # Calculer le nombre de colonnes que nous attendons après GameName
                        # C'est important pour savoir combien de parties sont censées être le GameName
                        num_cols_after_game_name = len(headers) - (game_name_index + 1)

                        # Si le nombre d'éléments dans la ligne est supérieur au nombre d'en-têtes,
                        # cela indique que GameName a été splitté par des virgules et n'était pas entre guillemets
                        if len(row) > len(headers):
                            # Les premières colonnes sont normales jusqu'à GameName
                            processed_row.extend(row[:game_name_index])

                            # Les dernières 'num_cols_after_game_name' colonnes sont les vraies colonnes après GameName
                            # Les éléments entre game_name_index et le début des dernières colonnes forment GameName
                            game_name_parts = row[game_name_index: len(row) - num_cols_after_game_name]
                            processed_row.append(','.join(game_name_parts))  # Rejoindre les parties du GameName

                            # Ajouter les colonnes restantes
                            processed_row.extend(row[len(row) - num_cols_after_game_name:])
                        else:
                            # La ligne a le nombre de colonnes attendu ou csv.reader a géré les guillemets
                            processed_row = row

                        # S'assurer que la ligne traitée a le bon nombre de colonnes avant de l'ajouter
                        if len(processed_row) == len(headers):
                            data_rows.append(processed_row)
                        else:
                            print(
                                f"Avertissement: Ligne {i + 2} ignorée dans {file.name} en raison d'un nombre incorrect de colonnes après traitement: {processed_row}")
                            print(f"Ligne originale problématique: {row}")

            # Créer le DataFrame à partir des lignes traitées
            if not data_rows:
                print(
                    f"Aucune donnée valide lue après le traitement spécial pour {file.name}. Le DataFrame sera vide ou basé sur pd.read_csv initial.")
                # Si GameName n'était pas dans les en-têtes, 'data' a déjà été créée par pd.read_csv.
                # Sinon, on initialise un DataFrame vide pour éviter une erreur.
                data = pd.DataFrame(columns=headers) if not headers else pd.DataFrame()
            else:
                data = pd.DataFrame(data_rows, columns=headers)

        except FileNotFoundError:
            print(f"Erreur: Le fichier {file} n'a pas été trouvé.")
            return
        except Exception as e:
            print(f"Une erreur est survenue lors de la lecture ou du traitement de {file}: {e}")
            print("Tentative de lecture avec pd.read_csv standard comme fallback...")


        data['categorie'] = str(categorie)
        data = pd.DataFrame(data, columns=['TerminalID', 'GameName', 'RaceNo', 'RaceDate', 'SelectedBets',
                                           'BetOption', 'TotalBets', 'BetAmount(CFA.)', 'TransactionDateTime',
                                           'CancelDateTime', 'categorie'])
        regex = r"\s*(\d{4}_\d{2}_\d{2})"
        format = "%Y_%m_%d"
        match = re.search(regex, file.name)
        date = match.group(1)
        converted_date = datetime.strptime(date, format)
        name = f"{self.name}_transformed_{categorie}_{converted_date.strftime('%Y-%m-%d')}.csv"
        self._save_file(file=file, data=data, type="csv", name=name, sep=';', encoding='latin-1', index=False)

    def _extract_zip_files(self):
        zip_files = self.source_path.glob("*.zip")
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.source_path)
            move_file(zip_file, self.zip_path)

    def _move_files(self):
        for file in  self.source_path.glob("*.csv"):
            if any(pat in file.name for pat in ["ALR_Payment"]):
                move_file(file, self.unused_files_path)

        for file in self.source_path.glob("*.csv"):
            if not any(pat in file.name for pat in ["ALR1", "ALR2", "ALR3"]):
                move_file(file, self.others_files_path)

    def process_transformation(self):
        self._extract_zip_files()
        self._move_files()
        self.logger.info(f"Transformation des fichiers de {self.source_path} en {self.file_pattern}")
        for file in self.source_path.glob(self.file_pattern):
            self.logger.info(f"Transformation du fichier {file}")
            if not check_file_not_empty(file): continue
            self._transform_file(file)
        pass


def run_gitech_physique_transformer():
    transformer = GitechPhysiqueTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_physique_transformer()