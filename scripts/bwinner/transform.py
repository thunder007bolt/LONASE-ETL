import os
import pandas as pd
import win32com.client
from datetime import datetime, timedelta
from pathlib import Path
from base.logger import Logger
from base.transformer import Transformer
from utils.config_utils import get_config
from utils.date_utils import get_yesterday_date
import sys


class BwinnerTransformer(Transformer):
    def __init__(self):
        super().__init__('bwinner', 'logs/transformer_bwinner.log')

    def _transform_file(self, file: Path):
        self.logger.info(f"Traitement du fichier : {file.name}")

        if file.suffix.lower() != ".xlsx":
            raise Exception(f"Type de fichier non géré : {file.name}")

        try:
            o = win32com.client.gencache.EnsureDispatch('Excel.Application')
        except Exception as e:
            sys.modules.pop('win32com.gen_py', None)
            self._transform_file(file)
            raise e

        o.Visible = False
        wb = o.Workbooks.Open(str(file.resolve()))
        csv_file = file.with_suffix(".csv")
        wb.SaveAs(str(csv_file.resolve()), FileFormat=24)
        wb.Close(SaveChanges=0)
        o.Quit()

        df = pd.read_csv(csv_file, sep=';')
        df = df[~df['Name'].isnull()]
        df = df[~df['Name'].str.contains("Totals", case=False)]

        delta = timedelta(days=1)
        df['Report Date'] = [(datetime.strptime(str(i)[:10], '%d/%m/%Y') + delta).strftime('%d/%m/%Y') for i in df['Report Date']]

        df = pd.DataFrame(df, columns=['Report Date', 'Name', 'Total Stakes', 'Total Paid Win'])

        self._save_file(file=csv_file, data=df, type="csv", index=False, sep=';', encoding='utf8')

def run_bwinner_transformer():
    transformer = BwinnerTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_bwinner_transformer()