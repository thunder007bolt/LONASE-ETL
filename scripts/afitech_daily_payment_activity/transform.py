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


class AfitechDailyPaymentActivityTransformer(Transformer):
    def __init__(self):
        super().__init__('afitech_daily_payment_activity', 'logs/transformer_afitech_daily_payment_activity.log')

    def _transform_file(self, file: Path, date=None):
        """
        """
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_excel(file, sheet_name='Data')

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        data = data.replace(np.nan, '')
        data['Partner'] = data['Partner'].str.replace(',', '.', regex=False)
        date = data['Date'][0].date()
        data['Date'] = data['Date'].dt.strftime('%d/%m/%Y')
        data = data.astype(str)

        filesInitialDirectory = r"K:\DATA_FICHIERS\AFITECH\DailyPaymentActivity\\"
        data.to_csv(filesInitialDirectory + "AFITECH_DailyPaymentActivity "+ date.strftime('%Y-%m-%d')+"_"+date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';')

        data = data.applymap(lambda x: str(x).replace('.', ','))
        data['t_amount_of_partner_deposits'] = 0
        data['t_am_of_partner_withdrawals'] = 0
        data.rename(
            {
                "Date": "jour",
                "Partner": "partner",
                "Payment Provider": "payment_provider",
                "Total Amount of Deposit": "total_amount_of_deposit",
                "Total Number of Deposit": "total_number_of_deposit",
                "Total Amount of Withdrawals": "total_amount_of_withdrawals",
                "Total Number of Withdrawals": "total_number_of_withdrawals",
                "Total Commissions": "total_commissions"
            }
        )

        self._save_file(file, data, type="csv", index=False, sep=';', encoding='utf8', reverse=True)


def run_afitech_daily_payment_activity_transformer():
    transformer = AfitechDailyPaymentActivityTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_afitech_daily_payment_activity_transformer()