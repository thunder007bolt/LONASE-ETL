import re
from pathlib import Path
import pandas as pd
from base.transformer import Transformer
from utils.excel_utils import convert_xls_to_xlsx


class GitechCasinoTransformer(Transformer):
    def __init__(self):
        super().__init__('gitech_casino', 'logs/transformer_gitech_casino.log')

    def extract_date_from_file(self, xlsx_file: Path) -> str:
        """
        Extrait la date contenue dans le fichier XLSX.
        """
        self.logger.info(f"Extraction de la date à partir du fichier {xlsx_file.name}")
        df = pd.read_excel(xlsx_file)
        cell_value = str(df.iloc[2])
        match = re.search(r"Du:\s*(\d{2}/\d{2}/\d{4})", cell_value)
        if match:
            return match.group(1)
        else:
            raise ValueError("Date non trouvée dans le fichier.")

    def process_numeric_column(self, value):
        """
        Nettoie et convertit une valeur numérique (retourne float pour casino).
        """
        value_str = str(value).replace(u'\xa0', '')
        if ',' in value_str:
            value_str = value_str.replace(',', '.')
        numeric_value = pd.to_numeric(value_str, errors='coerce')
        if pd.isna(numeric_value):
            return 0
        return numeric_value


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
            data = pd.read_excel(xlsx_file, skiprows=range(0, 6))
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
        data.columns = ['No', 'IdJeu', 'NomJeu', 'Vente', 'Paiement', 'PourcentagePaiement']
        
        # Suppression des lignes indésirables
        data = data[~data['NomJeu'].isin(['Total', 'montant global', 'PMU Online', 'Nom de jeu'])]
        
        # Suppression de la colonne 'No'
        data.drop('No', axis=1, inplace=True)
        
        # Insertion de la date
        data.insert(2, "Date vente", date_str)

        # Nettoyage des colonnes numériques
        numeric_cols = ['Vente', 'Paiement']
        for col in numeric_cols:
            data[col] = data[col].apply(self.process_numeric_column)

        # Suppression du fichier temporaire
        if xlsx_file != file:
            xlsx_file.unlink()

        # Sauvegarde (chemins hardcodés à nettoyer plus tard)
        if date:
            filesInitialDirectory = r"K:\DATA_FICHIERS\GITECH\CASINO\\"
            data.to_csv(filesInitialDirectory + "GITECH CASINO " + date.strftime('%Y-%m-%d') + ".csv",
                       index=False, sep=';', encoding='utf8')

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)


def run_gitech_casino_transformer():
    transformer = GitechCasinoTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_casino_transformer()