import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()

class VirtualAmabelLoad(Loader):
    def __init__(self):
        name = ('virtual_amabel')
        log_file = 'logs/loader_virtual_amabel.log'
        columns = [
            "nom",
            "total enjeu",
            "total ticket virtuel",
            "total paiement",
            "date vente"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_virtual_amabel_loader():
    loader = VirtualAmabelLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_virtual_amabel_loader()
