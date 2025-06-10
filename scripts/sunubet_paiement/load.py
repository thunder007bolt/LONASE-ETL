import pandas as pd, numpy as np
from base.loader2 import Loader
from utils.other_utils import load_env

load_env()


class SunubetPaiementLoad(Loader):
    def __init__(self, ):
        name = 'sunubet_paiement'
        log_file = 'logs/loader_sunubet_paiement.log'
        super().__init__(name, log_file)
        columns = [
            "fournisseur",
            "jour",
            "annee",
            "mois",
            "nombre_depots",
            "montant_depots",
            "nombre_retraits",
            "montant_retraits"
        ]

        # Oracle
        self.oracle_columns = columns
        self.oracle_table_name = "OPTIWARETEMP.SRC_PRD_SUNUBET_DEPOT_RETRAIT"

        # Sql server
        self.sql_server_columns = columns
        self.sql_server_table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_DEPOT_RETRAIT]"

    def _convert_file_to_dataframe(self, file):
        df = pd.read_excel(file, dtype=str)
        return df


def run_sunubet_paiement_loader():
    loader = SunubetPaiementLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_sunubet_paiement_loader()
