from pathlib import Path
import numpy as np
import pandas as pd
from base.tranformer import Transformer
from datetime import datetime, timedelta
from utils.file_manipulation import move_file, copy_files


class HonoreGamingTransformer(Transformer):
    def __init__(self):
        super().__init__('honore_gaming_new', 'logs/transformer_honore_gaming_new.log')

    def _transform_file(self, file: Path, date=None):
        path = r"K:\DATA_FICHIERS\HONORE_GAMING\\"
        ticket_path = r"K:\ETL\DATA_FICHIERS\honore_gaming_ticket\extracted\\"
        def renommer_fichier(nom_original):
            """
            Renomme un fichier comme demandé :
            Ex: honore_gaming_new_2025-08-05.csv -> daily-modified-horse-racing-tickets-detailed_20250805.csv
            """
            try:
                # Extraire la date dans le nom de fichier (au format YYYY-MM-DD)
                date_str = nom_original.split('_')[-1].replace('.csv', '')
                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                nouvelle_date = (date_obj + timedelta(days=1)).strftime("%Y%m%d")

                return f"daily-modified-horse-racing-tickets-detailed_{nouvelle_date}.csv"
            except Exception as e:
                raise ValueError(f"Erreur lors du renommage du fichier {nom_original} : {e}")

        copy_files(file.name, self.source_path, path, self.logger, rename_function=renommer_fichier)
        copy_files(file.name, self.source_path, ticket_path, self.logger)
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

        self._save_file(file, data, type='csv', index=False, sep=";", reverse=True, encoding='utf8')


def run_honore_gaming_new_transformer():
    transformer = HonoreGamingTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_honore_gaming_new_transformer()
