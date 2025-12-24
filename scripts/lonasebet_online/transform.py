from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class LonasebetOnlineTransformer(SimpleCSVTransformer):
    def __init__(self):
        super().__init__(
            name='lonasebet_online',
            log_file='logs/transformer_lonasebet_online.log',
            csv_sep=';',
            csv_encoding='utf-8',
            add_date_columns=True,
            select_columns=["BetId", "JOUR", "Stake", "BetCategory", "State", "PaidAmount", "CustomerLogin", "Freebet"],
            archive_path=r"K:\DATA_FICHIERS\LONASEBET\ALR_PARIFOOT\\"
        )


def run_lonasebet_online_transformer():
    transformer = LonasebetOnlineTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_lonasebet_online_transformer()
