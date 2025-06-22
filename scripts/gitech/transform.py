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

        clear_temp()

        self.logger.info(f"Conversion du fichier XLS {xls_file.name} en XLSX...")
        import xlwings as xw
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

        return xlsx_file

    def extract_date_from_file(self, xlsx_file: Path) -> str:

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

    def _transform_file(self, file: Path, date=None):
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

        data.columns = ['No', 'Agences', 'Operateur', 'Vente', 'Annulation',
                        'Remboursement', 'Paiement', 'Resultat']
        data = data[~data['Operateur'].isin(['Total', 'montant global'])]
        if 'No' in data.columns:
            data.drop('No', axis=1, inplace=True)
        data.insert(2, "Date vente", date_str)
        data['Agences'] = data['Agences'].ffill()
        numeric_cols = ['Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']
        for col in numeric_cols:
            data[col] = data[col].apply(self.process_numeric_column)

        xlsx_file.unlink()

        filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\ALR\\"
        data.to_csv(filesInitialDirectory + "GITECH "+ date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';',encoding='utf8')

        self._save_file(file=file, data=data, type="csv", sep=';',encoding='utf8', index=False)

def run_gitech_transformer():
    transformer = GitechTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_transformer()