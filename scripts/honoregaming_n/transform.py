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


class HonoreGamingTransformer(Transformer):
    def __init__(self):
        super().__init__('honore_gaming', 'logs/transformer_honore_gaming.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)
            data = pd.read_csv(file, sep=';', index_col=False)

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return
        # todo: get date from file or current date
        data = pd.DataFrame(data, columns=['ReportDateTime', 'TicketNumber', 'State', 'IssueDateTime',
                                           'TerminalId', 'TerminalDescription', 'RetailCategoryName',
                                           'RetailCategoryDescription', 'AgentId', 'AgentName', 'PaymentDateTime',
                                           'PaymentTerminalId', 'PaymentTerminalDescription',
                                           'PaymentRetailCategoryName', 'PaymentRetailCategoryDescription',
                                           'PaymentAgentId', 'PaymentAgentName', 'CancelDateTime',
                                           'CancelTerminalId', 'CancelTerminalDescription',
                                           'CancelRetailCategoryName', 'CancelRetailCategoryDescription',
                                           'CancelAgentId', 'CancelAgentName', 'CancelAdministratorLogin',
                                           'MeetingDate', 'MeetingNumber', 'RaceNumber', 'BetCategoryName',
                                           'BetType', 'Selection', 'MultiValue', 'TotalStake', 'PayableAmount',
                                           'PaidAmount', 'GameName'])

        data = data.replace(np.nan, '')
        data = data.astype(str)

        # Construction du nom du fichier CSV de sortie
        # Todo: setup dates
        csv_filename = f"HonoreGaming.csv"
        output_file = self.transformation_dest_path / csv_filename

        try:
            if output_file.exists():
                output_file.unlink()
            data.to_csv(output_file, index=False, sep=';', encoding='utf8')
            move_file(file, self.processed_dest_path)
            self.logger.info(f"Le fichier {csv_filename} a été transformé et sauvegardé avec succès.")

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la sauvegarde du fichier {csv_filename} : {e}")
            return

def run_honore_gaming_transformer():
    transformer = HonoreGamingTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_honore_gaming_transformer()
