import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class LonasebetCasinoLoad(Loader):
    def __init__(self):
        name = ('lonasebet_casino')
        log_file = 'logs/loader_lonasebet_casino.log'
        columns = [
            "date",
            "mise totale",
            "Somme PayÃ©e"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_LONASEBET]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_lonasebet_casino_loader():
    loader = LonasebetCasinoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_lonasebet_casino_loader()
