import os
import pandas as pd
import win32com.client
from datetime import datetime, timedelta
from pathlib import Path
from base.logger import Logger
from base.tranformer import Transformer
from utils.config_utils import get_config
from utils.date_utils import get_yesterday_date
import sys


class BwinnerTransformer(Transformer):
    def __init__(self):
        super().__init__('bwinner', 'logs/transformer_bwinner.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")

        df = pd.read_excel(file, sheet_name="Data",usecols=["Date", "Operator", "Channel","Total Stake","Total Paid Amount"])
        col_renames= {
            "Date":"Report Date",
            "Total Stake":"Total Stakes",
            "Total Paid Amount": "Total Paid Win"
        }
        df = df.rename(columns=col_renames)

        df = df[df['Operator'].str.contains("Bwinners")]
        df['Name'] = df['Channel'].apply(lambda x: 'sn.bwinner.net' if x == "Online" else 'physique')

        delta = timedelta(days=1)
        df['Report Date'] = [(datetime.strptime(str(i)[:10], '%d/%m/%Y') + delta).strftime('%d/%m/%Y') for i in df['Report Date']]

        df = pd.DataFrame(df, columns=['Report Date', 'Name', 'Total Stakes', 'Total Paid Win'])


        self._save_file(file=file, data=df, type="csv", index=False, sep=';', encoding='utf8')

def run_bwinner_transformer():
    transformer = BwinnerTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_bwinner_transformer()