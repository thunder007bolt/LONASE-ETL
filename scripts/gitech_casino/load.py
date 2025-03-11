import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class GitechCasinoLoad(Loader):
    def __init__(self):
        name = ('gitech_casino')
        log_file = 'logs/loader_gitech_casino.log'
        columns = ["idjeu", "nomjeu", "datevente", "vente", "paiement", "pourcentagepaiement"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_GITECH]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_gitech_casino_loader():
    loader = GitechCasinoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_gitech_casino_loader()