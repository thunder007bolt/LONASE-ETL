from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class MinishopLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='minishop',
            log_file='logs/loader_minishop.log',
            sql_columns=[
                "date",
                "etablissement",
                "jeu",
                "terminal",
                "vendeur",
                "montant a verser",
                "montant a payer"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_MINI_SHOP]",
            csv_sep=';',
            csv_encoding='latin-1',
            csv_dtype=str
        )

def run_minishop_loader():
    loader = MinishopLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_minishop_loader()
