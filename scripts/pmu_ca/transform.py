import os
import re
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import win32com.client
from datetime import datetime
from base.logger import Logger
from base.tranformer import Transformer
from utils.config_utils import get_config
from utils.file_manipulation import move_file


class PmuCATransformer(Transformer):
    def __init__(self, config_path=None, log_file=None):
        super().__init__('pmu_ca', log_file or 'logs/transformer_pmu_ca.log', config_path=config_path)

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_csv(file, sep=';', index_col=False)

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return
        # todo: get date from file or current date
        data = pd.DataFrame(data, columns=['PRODUIT','CA','SHARING','JOUR','ANNEE','MOIS'])

        data = data.replace(np.nan, '')
        data = data.astype(str)

        date = self._get_file_date(file)
        date = date.strftime("%Y-%m-%d")
        filename = "Pmu_Senegal_ca_" + str(date) + ".csv"

        filesInitialDirectory = r"K:\DATA_FICHIERS\PMUSENEGAL\\"
        data.to_csv(filesInitialDirectory + filename, index=False, sep=';')

        self._save_file(file, data, type="csv", index=False, sep=";")

def run_pmu_ca_transformer(config_path=None, log_file=None):
    transformer = PmuCATransformer(config_path=config_path, log_file=log_file)
    transformer.process_transformation()


if __name__ == '__main__':
    run_pmu_ca_transformer()
