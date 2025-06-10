import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class PmuCALoad(Loader):
    def __init__(self):
        name = ('pmu_ca')
        log_file = 'logs/loader_pmu_ca.log'
        columns = [
            "produit",
            "ca",
            "sharing",
            "jour",
            "annee",
            "mois"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PMUSENEGAL_CA]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df


def run_pmu_ca_loader():
    loader = PmuCALoad()
    loader.process_loading()


if __name__ == "__main__":
    run_pmu_ca_loader()
