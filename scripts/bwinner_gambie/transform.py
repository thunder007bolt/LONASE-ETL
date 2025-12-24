from pathlib import Path
import numpy as np
import pandas as pd
from base.transformer import Transformer
from utils.excel_utils import convert_xls_to_xlsx
from utils.data_cleaning_utils import clean_numeric_value


class BwinnerGambieTransformer(Transformer):
    def __init__(self):
        super().__init__('bwinner_gambie', 'logs/transformer_bwinner_gambie.log')

    def process_numeric_column(self, value):
        return clean_numeric_value(value)

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            if file.suffix.lower() == ".xls":
                xlsx_file = convert_xls_to_xlsx(file, self.logger)
                self.logger.info(f"Conversion de {file.name} en {xlsx_file.name} réussie.")
            elif file.suffix.lower() == ".xlsx":
                xlsx_file = file
            else:
                raise Exception(f"Type de fichier non géré : {file.name}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion de {file.name} : {e}")
            self.set_error(file.name)
            return

        try:
            data = pd.read_excel(xlsx_file, skiprows=range(0, 6))
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {xlsx_file.name} : {e}")
            return

        # Renommage des colonnes
        data.columns = ['No', 'Agences', 'Operateurs', 'date de vente', 'Recette', 'Annulation',
                       'Ventes Resultant', 'comm vente', 'Paiements', 'Resultats']

        # Suppression des 6 dernières lignes
        data = data[:-6]

        # Nettoyage
        data['Operateurs'] = data['Operateurs'].replace(np.nan, '')

        # Nettoyage des colonnes numériques
        numeric_cols = ['Operateurs', 'Recette', 'Annulation', 'Ventes Resultant', 'comm vente', 'Paiements', 'Resultats']
        for col in numeric_cols:
            data[col] = data[col].apply(self.process_numeric_column)

        # Formatage de la date
        data['date de vente'] = [str(i)[:10] for i in data['date de vente']]

        # Sélection et réorganisation des colonnes
        data = pd.DataFrame(data, columns=['No', 'Agences', 'Operateurs', 'date de vente', 'Recette', 'Annulation',
                                          'Ventes Resultant', 'comm vente', 'Paiements', 'Resultats'])

        data = data.replace(np.nan, '')
        data = data.astype(str)

        # Suppression du fichier temporaire
        if xlsx_file != file:
            xlsx_file.unlink()

        # Sauvegarde (chemins hardcodés à nettoyer plus tard)
        if date:
            filesInitialDirectory = r"K:\DATA_FICHIERS\BWINNERS_GAMBIE\\"
            data.to_csv(filesInitialDirectory + "BWINNER_GAMBIE_" + date.strftime('%Y-%m-%d') + ".csv",
                       index=False, sep=';', encoding='utf8')

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)

def run_bwinner_gambie_transformer():
    transformer = BwinnerGambieTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_bwinner_gambie_transformer()