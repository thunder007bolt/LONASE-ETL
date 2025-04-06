import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class PmuLotsLoad(Loader):
    def __init__(self):
        name = ('pmu_lots')
        log_file = 'logs/loader_pmu_lots.log'
        columns = [
            "joueur",
            "nombre de fois gagne",
            "montant",
            "type",
            "combinaison",
            "offre",
            "produit",
            "jour",
            "annee",
            "mois"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PMUSENEGAL_LOTS]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df


def run_pmu_lots_loader():
    loader = PmuLotsLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_pmu_lots_loader()
