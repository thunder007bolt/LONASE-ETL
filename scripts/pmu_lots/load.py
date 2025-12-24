from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class PmuLotsLoad(CSVLoader):
    def __init__(self, log_file=None, config_path=None):
        super().__init__(
            name='pmu_lots',
            log_file=log_file or 'logs/loader_pmu_lots.log',
            sql_columns=[
                "joueur",
                "nombre de fois gagne",
                "montant",
                "type",
                "combinaison",
                "offre",
                "produit",
                "jour",
                "annee",
                "mois"
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PMUSENEGAL_LOTS]",
            csv_sep=';',
            csv_encoding='utf-8',
            config_path=config_path
        )


def run_pmu_lots_loader(config_path=None, log_file=None):
    loader = PmuLotsLoad(config_path=config_path, log_file=log_file)
    loader.process_loading()


if __name__ == "__main__":
    run_pmu_lots_loader()
