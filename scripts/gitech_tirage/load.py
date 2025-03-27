import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class GitechTirageLoad(Loader):
    def __init__(self):
        name = ('gitech_tirage')
        log_file = 'logs/loader_gitech_tirage.log'
        columns = ["date_vente", "caption", "montant", "agence", "vendeur", "jeu"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_INSTANTANES]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, encoding='latin-1')
        return df

def run_gitech_tirage_loader():
    loader = GitechTirageLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_gitech_tirage_loader()