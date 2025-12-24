from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class SunubetonlineTransformer(SimpleCSVTransformer):
    def __init__(self):
        super().__init__(
            name='sunubet_online',
            log_file='logs/transformer_sunubet_online.log',
            csv_sep=';',
            csv_encoding='utf-8',
            add_date_columns=True,
            select_columns=["JOUR", "Stake", "PaidAmount", "BetCategory", "Freebet"],
            archive_path=r"K:\DATA_FICHIERS\SUNUBET\ONLINE\\"
        )
    
    def _transform_file(self, file: Path, date=None):
        if date is None:
            date = self._get_file_date(file, reverse=True)
        super()._transform_file(file, date)


def run_sunubet_online_transformer():
    transformer = SunubetonlineTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_sunubet_online_transformer()
