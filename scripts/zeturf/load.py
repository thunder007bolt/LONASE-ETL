from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class ZeturfLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='zeturf',
            log_file='logs/loader_zeturf.log',
            sql_columns=["hippodrome", "course", "depart", "paris", "enjeux", "annulations", "marge", "date_du_depart"],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ZETURF]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_zeturf_loader():
    loader = ZeturfLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_zeturf_loader()