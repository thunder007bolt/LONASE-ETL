import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()
from utils.file_manipulation import move_file


class AfitechDailyPaymentActivityLoad(Loader):
    def __init__(self):
        name = ('afitech_betting_operation')
        log_file = 'logs/loader_afitech_betting_operation.log'
        columns = [
            "date_time",
            "betting_operation_ref",
            "operator",
            "game_type",
            "state",
            "stake",
            "paid_amount"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_AFITECH_BETTING_OPERATION]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file,sep=';',index_col=False)

        return df
    def _load_datas(self, data):
        self.logger.info("Chargement des données dans la base...")
        insert_query = f"""
            INSERT INTO {self.table_name} ({", ".join([f'[{col}]' for col in self.columns])})
            VALUES
                ({", ".join(["?"] * len(self.columns))})
        """
        self.cursor.fast_executemany = True
        self.cursor.executemany(insert_query, data)
        self.connexion.commit()

        self.logger.info("Données chargées avec succès dans la base.")
    def process_loading(self):
        self._connection_to_db()
       # self._delete_table_datas()
        for file in self.source_path.glob(self.file_pattern):
            try:
                df = self._convert_file_to_dataframe(file)
                tuples_data = self._dataframe_to_tuples(df)
                self._load_datas(tuples_data)
                move_file(file, self.loaded_path)
                self.logger.info(f"Fichier {file} traité avec succès.")

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du fichier {file} : {e}")
                move_file(file, self.error_path)

def run_afitech_betting_operation_loader():
    loader = AfitechDailyPaymentActivityLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_afitech_betting_operation_loader()