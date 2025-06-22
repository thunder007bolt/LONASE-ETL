import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class AfitechCommissionHistoryLoad(Loader):
    def __init__(self):
        name = ('afitech_commission_history')
        log_file = 'logs/loader_afitech_commission_history.log'
        columns = [
            "debut_periode",
            "fin_periode",
            "partner",
            "payement_provider",
            "total_commisson",
            "deposit_total_amount",
            "deposit_count",
            "withdrawal_total_amount",
            "withdrawal_count"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_AFITECH_COMMISSION]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_afitech_commission_history_loader():
    loader = AfitechCommissionHistoryLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_afitech_commission_history_loader()
