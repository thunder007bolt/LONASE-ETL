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


class LonasebetOnlineTransformer(Transformer):
    def __init__(self):
        super().__init__('lonasebet_online', 'logs/transformer_lonasebet_online.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            data = pd.read_csv(file, sep=';',index_col=False)

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return
        # todo: get date from file or current date
        date = self._get_file_date(file)
        data["JOUR"] = str(date.strftime("%d/%m/%Y"))
        data["ANNEE"] = str(date.strftime("%Y"))
        data["MOIS"] = str(date.strftime("%m"))
        data = pd.DataFrame(data,columns=["BetId","JOUR","Stake","BetCategory","State","PaidAmount","CustomerLogin","Freebet"])
        data = data.replace(np.nan, '')
        data = data.astype(str)

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)


def run_lonasebet_online_transformer():
    transformer = LonasebetOnlineTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_lonasebet_online_transformer()
