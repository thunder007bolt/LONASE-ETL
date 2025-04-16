import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class AcajouDigitalLoad(Loader):
    def __init__(self):
        name = ('acajou_digital')
        log_file = 'logs/loader_acajou_digital.log'
        columns = ["date_heure", "reference_ticket", "telephone", "purchase_method", "montant", "lots_a_payes", "status", "produit"]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ACACIA]"
        super().__init__(name, log_file, columns, table_name)

    def _delete_table_datas(self):
        self.logger.info(f"Suppression des données dans la table")
        self.cursor.execute("""
        DELETE FROM [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ACACIA]
        WHERE produit NOT IN ('Pick3', 'Grattage')
        """)
        self.connexion.commit()

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        df['Gross Payout'] = df['Gross Payout'].astype(float).round(2).astype(str)
        return df

def run_acajou_digital_loader():
    loader = AcajouDigitalLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_acajou_digital_loader()