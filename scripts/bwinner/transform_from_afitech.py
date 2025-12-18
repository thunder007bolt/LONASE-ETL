import os
import pandas as pd
import win32com.client
from datetime import datetime, timedelta
from pathlib import Path
from base.logger import Logger
from base.tranformer import Transformer
from utils.config_utils import get_config
from utils.date_utils import get_yesterday_date, date_string_to_date
import sys


class BwinnerTransformer(Transformer):
    def __init__(self):
        super().__init__('bwinner', 'logs/transformer_bwinner.log')
        _, _, _, date = get_yesterday_date()
        # self.file_pattern = '*'+date.strftime('%d-%m-%Y')+'*'
        # self.file_pattern = '*01-02-2025*'

    def _transform_file(self, file: Path, start_date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")

        df = pd.read_excel(file, sheet_name="Data", dtype={"Date": str},
                           usecols=["Date", "Operator", "Channel", "Total Stake", "Total Paid Amount"])
        col_renames = {
            "Date": "Report Date",
            "Total Stake": "Total Stakes",
            "Total Paid Amount": "Total Paid Win"
        }
        df = df.rename(columns=col_renames)

        df = df[df['Operator'].str.contains("Bwinners")]
        df['Name'] = df['Channel'].apply(lambda x: 'sn.bwinners.net' if x == "Online" else 'physique')

        df = df.groupby('Channel', as_index=False).agg({
            'Report Date': 'first',
            'Operator': 'first',
            'Name': 'first',
            'Total Stakes': 'sum',
            'Total Paid Win': 'sum'
        })

        df = df.drop(columns=['Channel'])

        df['Report Date'] = [(datetime.strptime(str(i)[:10], '%Y-%m-%d')).strftime('%d/%m/%Y') for i in
                             df['Report Date']]

        df = pd.DataFrame(df, columns=['Report Date', 'Name', 'Total Stakes', 'Total Paid Win'])
        import numpy as np
        df['Total Stakes'] = df['Total Stakes'].round(0).astype(np.int64)
        df['Total Paid Win'] = df['Total Paid Win'].round(0).astype(np.int64)
        filesInitialDirectory = r"K:\DATA_FICHIERS\BWINNERS\\"
        df.to_csv(filesInitialDirectory + "Bwinner_" + str(start_date) + "_" + str(start_date) + ".csv", index=False,
                     sep=';', columns=['Report Date', 'Name', 'Total Stakes', 'Total Paid Win'])

        self._save_file(file=file, data=df, type="csv", is_multiple=True, reverse=True, index=False, sep=';',
                        encoding='utf8', move=False)

    def process_transformation(self):
        _, _, _, yesterday_date = get_yesterday_date()
        import os
        self.start_date =  date_string_to_date(os.getenv("transformed_start_date")) or self.config.get("transformed_start_date") or yesterday_date
        self.end_date = date_string_to_date(os.getenv("transformed_end_date")) or self.config.get("transformed_end_date") or yesterday_date
        start_date = self.start_date
        # todo: +1 if include_sup equals true
        end_date = self.start_date
        delta = timedelta(days=1)
        while end_date <= self.end_date:
            self.file_pattern = '*' + start_date.strftime('%d-%m-%Y') + '*xlsx'
            for file in self.source_path.glob(self.file_pattern):
                self.logger.info(f"Transformation du fichier {file}")
                self._transform_file(file, start_date)
            pass
            start_date += delta
            end_date += delta


def run_bwinner_transformer():
    transformer = BwinnerTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_bwinner_transformer()
