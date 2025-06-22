import pandas as pd, numpy as np
from base.loader2 import Loader
from utils.other_utils import load_env
load_env()

class BwinnerLoad(Loader):
    def __init__(self):
        name = ('bwinner')
        log_file = 'logs/loader_bwinner.log'
        columns = ["create_time", "product", "stake", "max payout"]
        super().__init__(name, log_file)

        self.oracle_columns = columns
        self.oracle_table_name = "OPTIWARETEMP.SRC_PRD_BWINNERS"

        self.sql_server_columns = columns
        self.sql_server_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS]"



    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, dtype=str)
        return df

def run_bwinner_loader():
    loader = BwinnerLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_bwinner_loader()