import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class AfitechDailyBettingLoad(Loader):
    def __init__(self):
        name = ('afitech_daily_betting')
        log_file = 'logs/loader_afitech_daily_betting.log'
        columns = [
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
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_AFITECH_DAILY_BETTING]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file,sep=';',index_col=False)
        return df

def run_afitech_daily_betting_loader():
    loader = AfitechDailyBettingLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_afitech_daily_betting_loader()