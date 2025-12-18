import pandas as pd, numpy as np
from base.loader2 import Loader
from utils.other_utils import load_env

load_env()


class MojabetUSSDAggrLoad(Loader):
    def __init__(self):
        name = ('mojabet_ussd_aggr')
        log_file = 'logs/loader_mojabet_ussd_aggr.log'
        super().__init__(name, log_file)

        columns = [
            "debut",
            "fin",
            "mois",
            "annee",
            "access_channel",
            "purchase_method",
            "collection",
            "gross_payout",
            "status",
            "disbursement",
            "produit"
        ]

        # Oracle
        self.oracle_columns = columns
        self.oracle_table_name = "OPTIWARETEMP.MOJABET_USSD"

        # Sql server
        self.sql_server_columns = columns
        self.sql_server_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[MOJABET_USSD]"

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, dtype=str)
        df['Gross Payout'] = df['Gross Payout'].astype(float).round(2).astype(str)
        return df

def run_mojabet_ussd_aggr_loader():
    loader = MojabetUSSDAggrLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_mojabet_ussd_aggr_loader()
