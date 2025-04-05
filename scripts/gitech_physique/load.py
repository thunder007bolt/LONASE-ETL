import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class GitechPhysiqueLoad(Loader):
    def __init__(self):
        name = ('gitech_physique')
        log_file = 'logs/loader_gitech_physique.log'
        columns = ["terminalid", "gamename", "raceno", "racedate", "selectedbets", "betoption", "totalbets","betamount_cfa", "transactiondatetime", "canceldatetime","categorie"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_GITECH_PARI_ALR]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, encoding='latin-1')
        return df

def run_gitech_physique_loader():
    loader = GitechPhysiqueLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_gitech_physique_loader()