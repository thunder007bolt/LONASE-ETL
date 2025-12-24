import os
import re
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import win32com.client
from datetime import datetime
from base.logger import Logger
from base.transformer import  Transformer
from utils.config_utils import get_config
from utils.file_manipulation import move_file


class AfitechDailyBettingTransformer(Transformer):
    def __init__(self):
        super().__init__('afitech_daily_betting', 'logs/transformer_afitech_daily_betting.log')

        # Colonnes autorisées
        self.allowed_columns = [
            "Date",
            "Operator",
            "Game type",
            "Channel",
            "Bet Count",
            "Total Stake",
            "Total Paid Amount",
            "Gross Gaming Revenue",
            "Tax Amount",
            "Open Stake"
        ]
    def _transform_file(self, file: Path, date=None):

        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_excel(file, sheet_name='Data')

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        data = data.replace(np.nan, '')

        # Filtrage des colonnes
        missing = [col for col in self.allowed_columns if col not in data.columns]

        if missing:
            self.logger.warning(
                f"Colonnes manquantes dans {file.name} : {missing}. "
                f"Elles seront remplies avec des valeurs vides."
            )
            for col in missing:
                data[col] = ""

        # Sélection dans l’ordre souhaité
        data = data[self.allowed_columns]
        self._save_file(file, data, type="csv", index=False, sep=';', encoding='utf8', reverse=True)
def run_afitech_daily_betting_transformer():
    transformer = AfitechDailyBettingTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_afitech_daily_betting_transformer()