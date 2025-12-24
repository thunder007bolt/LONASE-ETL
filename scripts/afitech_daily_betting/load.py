from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class AfitechDailyBettingLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='afitech_daily_betting',
            log_file='logs/loader_afitech_daily_betting.log',
            sql_columns=[
                "date",
                "operator",
                "game_type",
                "channel",
                "bet_count",
                "total_stake",
                "total_paid_amount",
                "gross_gaming_revenue",
                "tax_amount",
                "open_stake"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_AFITECH_DAILY_BETTING]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_afitech_daily_betting_loader():
    loader = AfitechDailyBettingLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_afitech_daily_betting_loader()