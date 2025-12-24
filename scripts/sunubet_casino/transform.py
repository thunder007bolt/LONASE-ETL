from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class SunubetCasinoTransformer(SimpleCSVTransformer):
    def __init__(self):
        super().__init__(
            name='sunubet_casino',
            log_file='logs/transformer_sunubet_casino.log',
            csv_sep=';',
            csv_encoding='utf-8',
            add_date_columns=True,
            select_columns=["JOUR", "Stake", "PaidAmount"],
            archive_path=r"K:\DATA_FICHIERS\SUNUBET\CASINO\\"
        )
    
    def _transform_file(self, file: Path, date=None):
        if date is None:
            date = self._get_file_date(file, reverse=True)
        super()._transform_file(file, date)

def run_sunubet_casino_transformer():
    transformer = SunubetCasinoTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_sunubet_casino_transformer()
