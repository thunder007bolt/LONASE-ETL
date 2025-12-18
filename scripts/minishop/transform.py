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


class MinishopTransformer(Transformer):
    def __init__(self):
        super().__init__('minishop', 'logs/transformer_minishop.log')

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            data = pd.read_csv(file, sep=';')

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        data.columns=['DATE', 'ETABLISSEMENT', 'JEU', 'TERMINAL', 'VENDEUR', 'MONTANT A VERSER', 'MONTANT A PAYER']

        filesInitialDirectory = r"K:\DATA_FICHIERS\MINI_SHOP\\"
        data.to_csv(filesInitialDirectory + "minishop_"+ date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';',encoding='latin-1' )

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='latin-1', index=False)


def run_minishop_transformer():
    transformer = MinishopTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_minishop_transformer()
