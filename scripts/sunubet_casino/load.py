from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class SunubetCasinoLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='sunubet_casino',
            log_file='logs/loader_sunubet_casino.log',
            sql_columns=[
                "issuedatetime",
                "stake",
                "paidamount"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_CASINO]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_sunubet_casino_loader():
    loader = LonasebetCasinoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_sunubet_casino_loader()
