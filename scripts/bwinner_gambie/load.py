import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class BwinnerGambieLoad(Loader):
    def __init__(self):
        name = ('bwinner_gambie')
        log_file = 'logs/loader_bwinner_gambie.log'
        columns = ["no", "agences", "operateurs", "date_de_vente", "recette", "annulation", "ventes_resultant", "comm_vente", "paiements", "resultats"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_BWINNERS_GAMBIE]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_bwinner_gambie_loader():
    loader = BwinnerGambieLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_bwinner_gambie_loader()