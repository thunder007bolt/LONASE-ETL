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


class BwinnerGambieTransformer(Transformer):
    def __init__(self):
        super().__init__('bwinner_gambie', 'logs/transformer_bwinner_gambie.log')

    def convert_xls_to_xlsx(self, xls_file: Path) -> Path:
        """
        Convertit un fichier XLS en XLSX via l'automatisation COM d'Excel.
        Après conversion, le fichier XLS d'origine est renommé avec un suffixe contenant la date
        et déplacé dans le répertoire des fichiers traités.
        """
        self.logger.info(f"Conversion du fichier XLS {xls_file.name} en XLSX...")
        excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
        wb = excel.Workbooks.Open(str(xls_file.resolve()))
        xlsx_file = xls_file.with_suffix(".xlsx")
        if xlsx_file.exists():
            xlsx_file.unlink()
        wb.SaveAs(str(xlsx_file.resolve()), FileFormat=51)
        wb.Close()
        excel.Application.Quit()


        # Renommage et déplacement du fichier XLS d'origine
        return xlsx_file

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

    def _transform_file(self, file: Path):
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
            data = pd.read_excel(xlsx_file, skiprows=range(0, 6))
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {xlsx_file.name} : {e}")
            return

        data.columns =  ['No','Agences','Operateurs','date de vente','Recette','Annulation','Ventes Resultant','comm vente','Paiements','Resultats']

        data = data[:-6]

        data['Operateurs'] = data['Operateurs'].replace(np.nan, '')

        numeric_cols = ['Operateurs', 'Recette', 'Annulation', 'Ventes Resultant', 'comm vente', 'Paiements', 'Resultats']
        for col in numeric_cols:
            data[col] = data[col].apply(self.process_numeric_column)

        data['date de vente'] = [ str(i)[:10] for i in data['date de vente'] ]

        data = pd.DataFrame(data,columns=['No', 'Agences', 'Operateurs', 'date de vente', 'Recette', 'Annulation','Ventes Resultant', 'comm vente', 'Paiements', 'Resultats'])

        data = data.replace(np.nan, '')
        data=data.astype(str)

        xlsx_file.unlink()

        self._save_file(file=file, data=data, type="csv", sep=';',encoding='utf8', index=False)

def run_bwinner_gambie_transformer():
    transformer = BwinnerGambieTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_bwinner_gambie_transformer()