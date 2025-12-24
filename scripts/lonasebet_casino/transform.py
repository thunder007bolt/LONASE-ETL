from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class LonasebetCasinoTransformer(SimpleCSVTransformer):
    def __init__(self):
        super().__init__(
            name='lonasebet_casino',
            log_file='logs/transformer_lonasebet_casino.log',
            csv_sep=';',
            csv_encoding='utf-8',
            add_date_columns=True,
            select_columns=["JOUR", "Stake", "PaidAmount"],
            archive_path=r"K:\DATA_FICHIERS\LONASEBET\CASINO\\"
        )
    
    def _transform_file(self, file: Path, date=None):
        # Utilise la logique de base
        if date is None:
            date = self._get_file_date(file)
        super()._transform_file(file, date)

def run_lonasebet_casino_transformer():
    transformer = LonasebetCasinoTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_lonasebet_casino_transformer()
