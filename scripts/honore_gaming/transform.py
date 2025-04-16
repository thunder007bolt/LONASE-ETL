from pathlib import Path
import numpy as np
import pandas as pd
from base.tranformer import Transformer
from utils.file_manipulation import move_file

class HonoreGamingTransformer(Transformer):
    def __init__(self):
        super().__init__('honore_gaming', 'logs/transformer_honore_gaming.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")
        try:
            # Lecture du fichier Excel en sautant les lignes d'en-tête (de la 2ème à la 6ème ligne)

            mylist = []

            for chunk in pd.read_csv(file, sep=';', index_col=False, chunksize=20000):
                mylist.append(chunk)

            data = pd.concat(mylist, axis=0)
            del mylist

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

        self._save_file(file, data, type='csv', index=False, sep=";", encoding='utf8')

def run_honore_gaming_transformer():
    transformer = HonoreGamingTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_honore_gaming_transformer()
