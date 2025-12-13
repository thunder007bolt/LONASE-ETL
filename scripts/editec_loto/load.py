import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class EditecLotoLoad(Loader):
    def __init__(self):
        name = ('editec_loto')
        log_file = 'logs/loader_editec_loto.log'
        columns = [
            "agentlogin",
            "retailcategory",
            "totalstake",
            "paidamount",
            "payableamount",
            "state",
            "jour",
            "annee",
            "mois"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_EDITEC_LOTO_NEW]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        df = df.replace(np.nan, 0)
        df = df.applymap(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
       # df['JOUR'] = pd.to_datetime(df['JOUR'], format='%d/%m/%Y')
        return df

def run_editec_loto_loader():
    loader = EditecLotoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_editec_loto_loader()
0