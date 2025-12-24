import pandas as pd
from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class BwinnerLoad(CSVLoader):
    def __init__(self):
        columns = ["create_time", "product", "stake", "max payout"]
        super().__init__(
            name='bwinner',
            log_file='logs/loader_bwinner.log',
            sql_columns=columns,
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS]",
            oracle_columns=columns,
            oracle_table_name="OPTIWARETEMP.SRC_PRD_BWINNERS",
            csv_sep=';',
            csv_encoding='utf-8',
            csv_dtype=str
        )


    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, dtype=str)
        return df

def run_bwinner_loader():
    loader = BwinnerLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_bwinner_loader()