import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class GitechParifootLoad(Loader):
    def __init__(self):
        name = ('gitech_parifoot')
        log_file = 'logs/loader_gitech_parifoot.log'
        columns = ["Agences", "Operateurs", "date_de_vente", "Recette_CFA", "Annulation_CFA", "Paiements_CFA"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_GITECH_PARIFOOT]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        df = df.replace(np.nan, '')
        df = pd.DataFrame(df,columns=['Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Paiement'])
        return df

def run_gitech_parifoot_loader():
    loader = GitechParifootLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_gitech_parifoot_loader()