import re
from pathlib import Path
import pandas as pd
from base.transformer import Transformer
from utils.excel_utils import convert_xls_to_xlsx
from utils.data_cleaning_utils import clean_numeric_value


class GitechTransformer(Transformer):
    def __init__(self):
        super().__init__('gitech', 'logs/transformer_gitech.log')

    def extract_date_from_file(self, xlsx_file: Path) -> str:
        """
        Extrait la date contenue dans le fichier XLSX.
        """
        self.logger.info(f"Extraction de la date à partir du fichier {xlsx_file.name}")
        df = pd.read_excel(xlsx_file)
        cell_value = str(df.iloc[1])
        match = re.search(r"Du:\s*(\d{2}/\d{2}/\d{4})", cell_value)
        if match:
            return match.group(1)
        else:
            raise ValueError("Date non trouvée dans le fichier.")

    def process_numeric_column(self, value):
        return clean_numeric_value(value)

    def _transform_file(self, file: Path, date=None):
        """
        Traite un fichier correspondant au motif "Etat de la course".
        """
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
            # Lecture du fichier Excel en sautant les lignes d'en-tête
            data = pd.read_excel(xlsx_file, skiprows=range(1, 6))
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {xlsx_file.name} : {e}")
            return

        try:
            date_str = self.extract_date_from_file(xlsx_file)
            self.logger.info(f"Date extraite : {date_str}")
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de l'extraction de la date de {xlsx_file.name} : {e}")
            return

        # Renommage des colonnes
        data.columns = ['No', 'Agences', 'Operateur', 'Vente', 'Annulation',
                        'Remboursement', 'Paiement', 'Resultat']
        
        # Suppression des lignes où 'Operateur' vaut 'Total' ou 'montant global'
        data = data[~data['Operateur'].isin(['Total', 'montant global'])]
        
        # Suppression de la colonne 'No'
        if 'No' in data.columns:
            data.drop('No', axis=1, inplace=True)
        
        # Insertion de la date
        data.insert(2, "Date vente", date_str)
        
        # Forward fill pour Agences
        data['Agences'] = data['Agences'].ffill()
        
        # Nettoyage des colonnes numériques
        numeric_cols = ['Vente', 'Annulation', 'Remboursement', 'Paiement', 'Resultat']
        for col in numeric_cols:
            data[col] = data[col].apply(self.process_numeric_column)

        # Suppression du fichier temporaire
        if xlsx_file != file:
            xlsx_file.unlink()

        # Sauvegarde (chemins hardcodés à nettoyer plus tard)
        if date:
            filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\ALR\\"
            data.to_csv(filesInitialDirectory + "GITECH " + date.strftime('%Y-%m-%d') + ".csv",
                       index=False, sep=';', encoding='utf8')

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)

def run_gitech_transformer():
    transformer = GitechTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_transformer()