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


class AcajouDigitalTransformer(Transformer):
    def __init__(self):
        super().__init__('acajou_digital', 'logs/transformer_acajou_digital.log')

    def _transform_file(self, file: Path, date):
        """
        """
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_csv(file, delimiter=',')
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        format = '%Y-%m-%d'
        data['Date Created'] = [datetime.strptime(i[:10], format).strftime('%d/%m/%Y') for i in data['Date Created']]
        data['Produit'] = str("Pari Sportif")
        data = pd.DataFrame(data, columns=['Date Created', 'Ticket ID', 'Msisdn', 'Purchase Method', 'Collection',
                                           'Gross Payout', 'Status', 'Produit'])
        data['Gross Payout'] = data['Gross Payout'].astype(float).round(2).astype(str)
        data = data.replace(np.nan, '')
        data = data.astype(str)

        filesInitialDirectory = r"K:\DATA_FICHIERS\ACAJOU\DIGITAIN\\"
        data.to_csv(filesInitialDirectory + "Listing_Tickets_Sports_betting "+ date.strftime('%Y%m%d') + "_"+date.strftime('%Y%m%d')+ ".csv", index=False,sep=';',encoding='utf8')

        self._save_file(file=file, data=data, type="csv", index=False, sep=';', encoding='utf8')


def run_acajou_digital_transformer():
    transformer = AcajouDigitalTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_acajou_digital_transformer()
