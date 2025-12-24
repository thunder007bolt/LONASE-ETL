from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()

class VirtualAmabelLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='virtual_amabel',
            log_file='logs/loader_virtual_amabel.log',
            sql_columns=[
                "nom",
                "total enjeu",
                "total ticket virtuel",
                "total paiement",
                "date vente"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET]",
            csv_sep=';',
            csv_encoding='utf-8'
        )

def run_virtual_amabel_loader():
    loader = VirtualAmabelLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_virtual_amabel_loader()
