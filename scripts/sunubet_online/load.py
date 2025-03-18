import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class SunubetOnlineLoad(Loader):
    def __init__(self):
        name = ('sunubet_online')
        log_file = 'logs/loader_sunubet_online.log'
        columns = [
            "issuedatetime",
            "stake",
            "paidamount",
            "betcategorytype",
            "freebet"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_ONLINE]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_sunubet_online_loader():
    loader = SunubetOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_sunubet_online_loader()
