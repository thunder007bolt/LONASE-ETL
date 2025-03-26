import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class ZeturfLoad(Loader):
    def __init__(self):
        name = ('zeturf')
        log_file = 'logs/loader_zeturf.log'
        columns = ["hippodrome", "course", "depart", "paris", "enjeux", "annulations", "marge", "date_du_depart"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ZETURF]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_zeturf_loader():
    loader = ZeturfLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_zeturf_loader()