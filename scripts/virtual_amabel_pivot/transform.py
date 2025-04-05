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
import xlwings as xw

class VirtualAmabelPivotTransformer(Transformer):
    def __init__(self):
        super().__init__('virtual_amabel_pivot', 'logs/transformer_virtual_amabel_pivot.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")
        wingsbook = xw.Book(file)
        wingsapp = xw.apps.active
        new_file = file.parent / f"renamed_{file.name}"
        wingsbook.save(new_file)
        wingsapp.quit()
        try:
            data =pd.read_excel(new_file, sheet_name=1, index_col=False)
        except Exception as e:
            self.set_error(new_file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        date = self._get_file_date(new_file)
        data["JOUR"] = str(date.strftime("%d/%m/%Y"))
        data["ANNEE"] = str(date.strftime("%Y"))
        data["MOIS"] = str(date.strftime("%m"))
        data = pd.DataFrame(data, columns=['Start date', 'End date', 'Client ID', 'Client name', 'Client ID (Ext)', 'Entity ID (Ext)', 'Entity ID',
                                      'Entity name', 'Entity played ID (Ext)', 'Entity played', 'Entity played name', 'Currency', 'Playlist',
                                      'Game', 'Market', 'Selection', 'Confirmed stake', 'Bet winnings', 'Paid Out', 'Number of bets', 'Timezone',
                                      'Combinations', 'Won bets', 'Bonus winnings', 'Local jackpot winnings', 'Local jackpot contribution',
                                      'Local jackpot payout', 'Network jackpot winnings', 'Network jackpot contribution',
                                      'Network jackpot payout', 'Cancelled stake', 'Played tickets', 'Cancelled tickets', 'Tags', 'get RTP',
                                      'Target balance', 'JOUR', 'ANNEE', 'MOIS'])
        data = data.replace(np.nan, '')
        data = data.astype(str)
        new_file.unlink()
        self._save_file(file, data, type="csv", index=False, sep=';')

def run_virtual_amabel_pivot_transformer():
    transformer = VirtualAmabelPivotTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_virtual_amabel_pivot_transformer()
