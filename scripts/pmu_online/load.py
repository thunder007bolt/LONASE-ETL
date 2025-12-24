from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class PmuOnlineLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='pmu_online',
            log_file='logs/loader_pmu_online.log',
            sql_columns=["s.no", "date", "nom de jeu", "ventes totales", "gains(CFA.)", 
                        "pourcentage de paiement(%)", "montant net(CFA.)"],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PMU_ONLINE_1]",
            csv_sep=';',
            csv_encoding='utf-8',
            csv_dtype=str
        )

def run_pmu_online_loader():
    loader = PmuOnlineLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_pmu_online_loader()