import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class LonasebetOnlineLoad(Loader):
    def __init__(self):
        name = ('lonasebet_online')
        log_file = 'logs/loader_lonasebet_online.log'
        columns = [
            "id",
            "issuedatetime",
            "stake",
            "betcategorytype",
            "state",
            "paidamount",
            "customerlogin",
            "freebet"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_LONASEBET]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_lonasebet_online_loader():
    loader = LonasebetOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_lonasebet_online_loader()
