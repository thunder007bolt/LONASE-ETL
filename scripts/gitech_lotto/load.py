from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class GitechLottoLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='gitech_lotto',
            log_file='logs/loader_gitech_lotto.log',
            sql_columns=["Agences", "Operateurs", "date_de_vente", "Recette_CFA", "Annulation_CFA", "Paiements_CFA"],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_GITECH_LOTO]",
            csv_sep=';',
            csv_encoding='utf-8'
        )
    
    def _convert_file_to_dataframe(self, file):
        df = super()._convert_file_to_dataframe(file)
        # Sélection des colonnes spécifiques
        df = df[['Agences', 'Operateur', 'Date vente', 'Vente', 'Annulation', 'Paiement']]
        return df

def run_gitech_lotto_loader():
    loader = GitechLottoLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_gitech_lotto_loader()