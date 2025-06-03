import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class BwinnerLoad(Loader):
    def __init__(self):
        name = ('bwinner')
        log_file = 'logs/loader_bwinner.log'
        columns = ["create_time", "product", "stake", "max payout"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, dtype=str)
        return df

def run_bwinner_loader():
    loader = BwinnerLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_bwinner_loader()