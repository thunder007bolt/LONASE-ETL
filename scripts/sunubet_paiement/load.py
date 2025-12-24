import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class SunubetPaiementLoad(Loader):
    def __init__(self):
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
        super().__init__(
            name='sunubet_paiement',
            log_file='logs/loader_sunubet_paiement.log',
            sql_columns=columns,
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_DEPOT_RETRAIT]",
            oracle_columns=columns,
            oracle_table_name="OPTIWARETEMP.SRC_PRD_SUNUBET_DEPOT_RETRAIT"
        )

    def _convert_file_to_dataframe(self, file):
        df = pd.read_excel(file, dtype=str)
        return df


def run_sunubet_paiement_loader():
    loader = SunubetPaiementLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_sunubet_paiement_loader()
