import os
import re
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import win32com.client
from datetime import datetime
from base.logger import Logger
from base.tranformer import  Transformer
from utils.config_utils import get_config


class GitechTransformer(Transformer):
    def __init__(self):
        super().__init__('gitech', 'logs/transformer_gitech.log')

    def convert_xls_to_xlsx(self, xls_file: Path) -> Path:
        TEMP_DIR = r"C:\Users\optiware2\AppData\Local\Temp\gen_py\3.7"
        def clear_temp():
            try:
                shutil.rmtree(TEMP_DIR)
            except OSError as o:
                print(f"Erreur : {o.strerror}")
        """
        Convertit un fichier XLS en XLSX via l'automatisation COM d'Excel.
        Après conversion, le fichier XLS d'origine est renommé avec un suffixe contenant la date
        et déplacé dans le répertoire des fichiers traités.
        """
        clear_temp()

        self.logger.info(f"Conversion du fichier XLS {xls_file.name} en XLSX...")
        import xlwings as xw
        # Lancement d'Excel (en arrière-plan)
        app = xw.App(visible=False)

        try:
            wb = app.books.open(str(xls_file.resolve()))
            xlsx_file = xls_file.with_suffix(".xlsx")

            if xlsx_file.exists():
                xlsx_file.unlink()

            wb.save(str(xlsx_file.resolve()))
            wb.close()
        finally:
            app.quit()

        # Renommage et déplacement du fichier XLS d'origine
        return xlsx_file

    def extract_date_from_file(self, xlsx_file: Path) -> str:
        """
        Extrait la date contenue dans le fichier XLSX. On suppose que la date se trouve dans la
        deuxième ligne (index 1) et correspond au format 'Du: DD/MM/YYYY'.
        """
        self.logger.info(f"Extraction de la date à partir du fichier {xlsx_file.name}")
        df = pd.read_excel(xlsx_file)
        cell_value = str(df.iloc[1])
        match = re.search(r"Du:\s*(\d{2}/\d{2}/\d{4})", cell_value)
        if match:
            date_str = match.group(1)
            return date_str
        else:
            raise ValueError("Date non trouvée dans le fichier.")

    def process_numeric_column(self, value):
        """
        Nettoie et convertit une valeur lue depuis une colonne numérique.
        - Suppression des espaces insécables.
        - Si une virgule est présente, suppression des zéros finaux et de la virgule.
        - Conversion en entier (les erreurs produisent un 0).
        """
        value_str = str(value).replace(u'\xa0', '')
        if ',' in value_str:
            value_str = value_str.rstrip('00').replace(',', '')
        try:
            numeric_value = pd.to_numeric(value_str, errors='coerce')
            if pd.isna(numeric_value):
                return 0
            return int(numeric_value)
        except Exception:
            return 0

    def _transform_file(self, file: Path, date):
        """
        Traite un fichier correspondant au motif "Etat de la course".
        Cette méthode effectue les étapes suivantes :
          - Conversion en XLSX si nécessaire
          - Lecture et nettoyage des données
          - Extraction de la date
          - Transformation des données et création du CSV de sortie
          - Suppression du fichier XLSX temporaire
        """
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            if file.suffix.lower() == ".xls":
                xlsx_file = self.convert_xls_to_xlsx(file)
                self.logger.info(f"Conversion de {file.name} en {xlsx_file.name} réussie.")
            elif file.suffix.lower() == ".xlsx":
                xlsx_file = file
            else:
                raise Exception(f"Type de fichier non géré : {file.name}")

        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion de {file.name} : {e}")
            self.set_error(file.name)
            # TODO : déplacer le fichier dans un dossier d'erreur
            return

        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_excel(xlsx_file, skiprows=range(1, 6))
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {xlsx_file.name} : {e}")
            return

        try:
            date_str = self.extract_date_from_file(xlsx_file)
            self.logger.info(f"Date extraite : {date_str}")

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de l'extraction de la date de {xlsx_file.name} : {e}")
            return

            # renommage des colonnes
            data.columns = ['No', 'Agences', 'Operateur', 'Vente', 'Annulation', 'Remboursement', 'Paiement',
                            'Resultat']

            # suppression de toutes les lignes comptenant Total et montant global
            data = data[data.Operateur != 'Total']
            data = data[data.Operateur != 'montant global']

            # suppression de la colonne No
            data = data.drop('No', axis=1)

            # insertion et remplissage de la colonne date suivant la date indiquée dans le fichier xls
            date_serie = pd.Series(np.random.randn(len(data)), index=data.index)
            data.insert(2, "Date vente", date_serie, True)
            data['Date vente'] = data['Date vente'].apply(lambda x: str(x).replace(str(x), str(date.replace("-", "/"))))

            # remplissage de la colonne Agence, les valeurs nulles sont remplies par leurs agences correspondantes

            data = data.copy(deep=True)

            v_agence = data['Agences'].iloc[0]
            for i in range(0, len(data), 1):
                # print(v_agence)
                if (pd.notnull(data['Agences'].iloc[i])):
                    v_agence = data['Agences'].iloc[i]
                else:
                    data['Agences'].iloc[i] = v_agence

            # Formattage des colonnes Vente, Annulation, Remboursement, Paiement, Resultat en numeric
            data['Resultat'] = data['Resultat'].map(lambda x: str(x).replace(u'\xa0', u''))
            data['Vente'] = data['Vente'].map(lambda x: str(x).replace(u'\xa0', u''))
            data['Annulation'] = data['Annulation'].map(lambda x: str(x).replace(u'\xa0', u''))
            data['Remboursement'] = data['Remboursement'].map(lambda x: str(x).replace(u'\xa0', u''))
            data['Paiement'] = data['Paiement'].map(lambda x: str(x).replace(u'\xa0', u''))

            data['Resultat'] = data['Resultat'].map(
                lambda x: str(x).rstrip('00').replace(',', '') if (re.search(",", str(x))) else str(x))
            data['Vente'] = data['Vente'].map(
                lambda x: str(x).rstrip('00').replace(',', '') if (re.search(",", str(x))) else str(x))

            data['Annulation'] = data['Annulation'].map(
                lambda x: str(x).rstrip('00').replace(',', '') if (re.search(",", str(x))) else str(x))
            data['Remboursement'] = data['Remboursement'].map(
                lambda x: str(x).rstrip('00').replace(',', '') if (re.search(",", str(x))) else str(x))
            data['Paiement'] = data['Paiement'].map(
                lambda x: str(x).rstrip('00').replace(',', '') if (re.search(",", str(x))) else str(x))

            data[['Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']] = data[
                ['Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']].astype('int64')

            # print(data.head())
            # print(data.tail())
        #filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\ALR\\"
        #data.to_csv(filesInitialDirectory + "GITECH "+ date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';',encoding='utf8')

        self._save_file(file=file, data=data, type="csv", sep=';',encoding='utf8', index=False)

def run_gitech_transformer():
    transformer = GitechTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_transformer()