import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class PmuOnlineLoad(Loader):
    def __init__(self):
        name = ('pmu_online')
        log_file = 'logs/loader_pmu_online.log'
        columns = ["s.no", "date", "nom de jeu", "ventes totales", "gains(CFA.)", "pourcentage de paiement(%)","montant net(CFA.)"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PMU_ONLINE_1]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False,dtype=str)
        return df

def run_pmu_online_loader():
    loader = PmuOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_pmu_online_loader()