import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class AfitechDailyPaymentActivityLoad(Loader):
    def __init__(self):
        name = ('afitech_daily_payment_activity')
        log_file = 'logs/loader_afitech_daily_payment_activity.log'
        columns = [
            "jour",
            "partner",
            "payment_provider",
            "total_amount_of_deposit",
            "total_number_of_deposit",
            "total_amount_of_withdrawals",
            "total_number_of_withdrawals",
            "total_commissions",
            "t_amount_of_partner_deposits",
            "t_am_of_partner_withdrawals"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_AFITECH_DAILYPAYMENT]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file,sep=';',index_col=False)

        return df

def run_afitech_daily_payment_activity_loader():
    loader = AfitechDailyPaymentActivityLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_afitech_daily_payment_activity_loader()