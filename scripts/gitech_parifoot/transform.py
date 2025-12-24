from pathlib import Path
import pandas as pd
from base.gitech_transformer import GitechBaseTransformer


class GitechParifootTransformer(GitechBaseTransformer):
    def __init__(self):
        super().__init__(
            name='gitech_parifoot',
            log_file='logs/transformer_gitech_parifoot.log',
            skiprows=6,
            date_pattern=r"date\s+de\s+début\s+de\s+la\s+vente\s*:\s*(\d{2}/\d{2}/\d{4})"
        )

    def _transform_file(self, file: Path, date=None):
        """
        Traite un fichier correspondant au motif "Etat de la course".
        """
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            xlsx_file = self._prepare_excel_file(file)
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion de {file.name} : {e}")
            self.set_error(file.name)
            return

        try:
            data = self._read_excel_data(xlsx_file)
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

        # Mapping des colonnes
        col_mapping = {
            'S.No': 'No',
            'Agences': 'Agences',
            'Operateurs': 'Operateur',
            'date de vente': 'Date vente',
            'Recette(CFA.)': 'Vente',
            'Annulation(CFA)': 'Annulation',
            'Ventes Resultant(CFA)': 'Ventes Resultant',
            'Paiements(CFA.)': 'Paiement',
            'Resultats(CFA.)': 'Resultat'
        }

        # Nettoyage commun (pattern spécifique à Parifoot)
        exclude_values = {
            'Date vente': ['Total', 'montant global'],
            'Agences': ['montant global', 'Nom de jeu']
        }
        exclude_patterns = [r'^Parifoot\(\d+(\.\d+)?%\)$']
        
        data = self._apply_common_cleaning(data, col_mapping, exclude_patterns, exclude_values)

        # Ajout de la colonne Remboursement
        data['Remboursement'] = 0

        # Sélection et réorganisation des colonnes
        columns = ['No', 'Agences', 'Operateur', 'Vente', 'Annulation',
                   'Remboursement', 'Paiement', 'Resultat']
        data = data[columns]

        # Exclusion supplémentaire
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
        data = self._process_numeric_columns(data, numeric_cols)

        # Suppression du fichier temporaire
        xlsx_file.unlink()

        # Sauvegarde
        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)

def run_gitech_parifoot_transformer():
    transformer = GitechParifootTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_parifoot_transformer()