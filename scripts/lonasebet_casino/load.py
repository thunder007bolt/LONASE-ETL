from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class LonasebetCasinoLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='lonasebet_casino',
            log_file='logs/loader_lonasebet_casino.log',
            sql_columns=[
                "date",
                "mise totale",
                "Somme PayÃ©e"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_LONASEBET]",
            csv_sep=';',
            csv_encoding='utf-8',
            csv_dtype=str
        )

def run_lonasebet_casino_loader():
    loader = LonasebetCasinoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_lonasebet_casino_loader()
