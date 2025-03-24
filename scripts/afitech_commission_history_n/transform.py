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
from utils.file_manipulation import move_file


class AfitechCommissionHistoryTransformer(Transformer):
    def __init__(self):
        super().__init__('commission_history', 'logs/transformer_afitech_commission_history.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            data = pd.read_excel(file, sheet_name='Data')

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        self._save_file(file, data, type="csv", is_multiple=True, reverse=True, index=False, sep=';', encoding='utf8')

def run_afitech_commission_history_transformer():
    transformer = AfitechCommissionHistoryTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_afitech_commission_history_transformer()