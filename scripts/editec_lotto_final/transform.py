from pathlib import Path
from datetime import datetime
from base.tranformer import Transformer
import datetime
from utils.date_utils import get_yesterday_date, date_string_to_date
import os


class GitechLottoTransformer(Transformer):
    def __init__(self):
        super().__init__('editec_lotto_final', 'logs/transformer_editec_lotto_final.log')
        self.start_date: datetime = self.config['start_date']
        self.end_date: datetime = self.config['end_date']

    def _set_date(self):
        _, _, _, yesterday_date = get_yesterday_date()
        self.logger.info( f" ENV START_DATE {os.getenv("start_date")}")
        self.logger.info( f" ENV END_DATE {os.getenv("end_date")}")
        self.start_date = date_string_to_date(os.getenv("start_date")) or self.start_date or  self.config.get("start_date") or yesterday_date
        self.end_date = date_string_to_date(os.getenv("end_date")) or self.end_date or self.config.get("end_date") or yesterday_date
        self.logger.info(f" SELF START_DATE {os.getenv("start_date")}")
        self.logger.info(f" SELF END_DATE {os.getenv("end_date")}")
    def process_transformation(self):
        self._set_date()
        date = self.start_date
        base_path = self.base_config['paths']['data_path']
        while date <= self.end_date:
            date_yyyy_mm_dd = date.strftime("%Y-%m-%d")
            pattern_lotto = Path(
                base_path + 'editec_loto_lots/transformed/editec_loto_lots_transformed_' + date_yyyy_mm_dd + '.csv')
            pattern_lotto_ca = Path(
                base_path + 'editec_loto/transformed/editec_loto_transformed_' + date_yyyy_mm_dd + '.csv')

            if pattern_lotto.exists() and pattern_lotto_ca.exists():
                import pandas as pd
                lotto_lots_df = pd.read_csv(pattern_lotto, sep=';')
                total_paiement = lotto_lots_df['TotalDrawGamePaidAmount'].sum()

                lotto_ca_df = pd.read_csv(pattern_lotto_ca, sep=';')
                lotto_ca_df['PaidAmount'] = 0

                lotto_ca_df.loc[0, 'PaidAmount'] = total_paiement

                name = 'editec_lotto_final_'+date_yyyy_mm_dd+'.csv'
                self._save_file2(data=lotto_ca_df, name=name, type="csv", sep=';', encoding='utf8', index=False)
                self.logger.info(f"{name} généré")
                date += datetime.timedelta(days=1)

            else:
                date += datetime.timedelta(days=1)
                continue


def run_editec_lotto_final_transformer():
    transformer = GitechLottoTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_editec_lotto_final_transformer()
