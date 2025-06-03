import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env
import numpy as np
load_env()


class USSDIRVLoad(Loader):
    def __init__(self):
        name = ('ussd_irv')
        log_file = 'logs/loader_ussd_irv.log'
        columns = [
            "dateappel",
            "jour",
            "numeroserveur",
            "numeroappelant",
            "dureeappel",
            "totalappels",
            "totalca"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[TEMP_USSD_IVR]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        df = df.replace(np.nan, '')
        return df


def run_ussd_irv_loader():
    loader = USSDIRVLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_ussd_irv_loader()
