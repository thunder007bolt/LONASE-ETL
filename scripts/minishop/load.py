import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class MinishopLoad(Loader):
    def __init__(self):
        name = ('minishop')
        log_file = 'logs/loader_minishop.log'
        columns = [
            "date",
            "etablissement",
            "jeu",
            "terminal",
            "vendeur",
            "montant a verser",
            "montant a payer"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_MINI_SHOP]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False, dtype=str)
        return df

def run_minishop_loader():
    loader = MinishopLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_minishop_loader()
