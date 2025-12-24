from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class SunubetOnlineLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='sunubet_online',
            log_file='logs/loader_sunubet_online.log',
            sql_columns=[
                "issuedatetime",
                "stake",
                "paidamount",
                "betcategorytype",
                "freebet"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_ONLINE]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_sunubet_online_loader():
    loader = SunubetOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_sunubet_online_loader()
