from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class LonasebetOnlineLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='lonasebet_online',
            log_file='logs/loader_lonasebet_online.log',
            sql_columns=[
                "id",
                "issuedatetime",
                "stake",
                "betcategorytype",
                "state",
                "paidamount",
                "customerlogin",
                "freebet"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_LONASEBET]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_lonasebet_online_loader():
    loader = LonasebetOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_lonasebet_online_loader()
