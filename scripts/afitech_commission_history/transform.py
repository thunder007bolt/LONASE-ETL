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
        super().__init__('afitech_commission_history', 'logs/transformer_afitech_commission_history.log')

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            data = pd.read_excel(file, sheet_name='Data')
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        data.columns = ['Début de la période', 'Fin de la période', 'Partner',
                      'Payement Provider', 'Total Commisson', 'Deposit Total Amount',
                      'Deposit Count', 'Withdrawal Total Amount', 'Withdrawal Count']
        data = data.replace(np.nan, '')
        data['Partner'] = data['Partner'].str.replace(',', '.', regex=False)

        start_date = data['Début de la période'][0].date()
        end_date = data['Fin de la période'][0].date()
        filesInitialDirectory = r"K:\DATA_FICHIERS\AFITECH\CommissionHistory\\"
        data = data.astype(str)
        data.to_csv(filesInitialDirectory + "AFITECH_CommissionHistory "+ start_date.strftime('%Y-%m-%d')+"_"+end_date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';')

        data = data.applymap(lambda x: str(x).replace('.', ','))

        data['Début de la période'] = data['Début de la période'].str.replace('-', '/', regex=False)  # Fin de la période
        data['Fin de la période'] = data['Fin de la période'].str.replace('-', '/', regex=False)
        self._save_file(file, data, type="csv", is_multiple=True, reverse=True, index=False, sep=';', encoding='utf8')

def run_afitech_commission_history_transformer():
    transformer = AfitechCommissionHistoryTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_afitech_commission_history_transformer()