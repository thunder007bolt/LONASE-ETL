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


class ParifootOnlineTransformer(Transformer):
    def __init__(self):
        super().__init__('parifoot_online', 'logs/transformer_parifoot_online.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_csv(file, sep=',', index_col=False)

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return
        # todo: get date from file or current date
        date = self._get_file_date(file)
        data['date'] = date.strftime('%d/%m/%Y')
        data = pd.DataFrame(data,columns=['Unnamed: 0','Username', 'Balance', 'Total Players','Total Players Date Range', 'SB Bets No.', 'SB Stake','SB Closed Stake', 'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds','SB GGR', 'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins','Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR', 'Adjustments','Deposits', 'Financial Deposits', 'Financial Withdrawals','Transaction Fee', 'date'])
        data = data.replace(np.nan, '')
        data=data.astype(str)

        self._save_file(file, data, type="csv", index=False, sep=';', encoding='utf8')



def run_parifoot_online_transformer():
    transformer = ParifootOnlineTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_parifoot_online_transformer()
