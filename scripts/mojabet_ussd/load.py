import pandas as pd
from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class MojabetUSSDLoad(CSVLoader):
    def __init__(self):
        columns = [
            "jour", "mois",
            "annee", "access_channel", "purchase_method", "collection",
            "gross_payout", "status", "disbursement", "produit"
        ]
        super().__init__(
            name='mojabet_ussd',
            log_file='logs/loader_mojabet_ussd.log',
            sql_columns=columns,
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[MOJABET_USSD_DAILY]",
            oracle_columns=columns,
            oracle_table_name="OPTIWARETEMP.MOJABET_USSD_DAILY",
            csv_sep=';',
            csv_encoding='utf-8',
            csv_dtype=str
        )

    def _convert_file_to_dataframe(self, file):
        df = super()._convert_file_to_dataframe(file)
        # Traitement spécifique pour Gross Payout
        if 'Gross Payout' in df.columns:
            df['Gross Payout'] = df['Gross Payout'].astype(float).round(2).astype(str)
        return df


def run_mojabet_ussd_loader():
    loader = MojabetUSSDLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_mojabet_ussd_loader()
