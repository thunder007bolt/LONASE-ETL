from pathlib import Path
import numpy as np
import pandas as pd
from base.tranformer import Transformer
from utils.config_utils import get_config

class LonasebetGlobalTransformer(Transformer):
    def __init__(self):
        super().__init__('lonasebet_global', 'logs/transformer_lonasebet_global.log')


    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            data = pd.read_csv(file, sep=';', encoding='latin1', dtype=str)
            self.logger.info(f"Fichier {file.name} lu. Nombre de lignes: {len(data)}, Nombre de colonnes: {len(data.columns)}")

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return
        cols = [
            "Nombre_de_paris", "Nombre_de_tickets", "Mises",
            "Produit_brut_des_jeux", "Rentabilite", "Mises_en_cours",
            "Gains_Joueurs", "Montant_total_a_payer", "Montant_total_paye",
            "Montant_a_payer_expire", "Produit_bruts_des_jeux_Cashed_Out",
            "JOUR", "ANNEE", "MOIS", "CANAL", "CATEGORIE"
        ]
        for col in cols:
            if col not in data.columns:
                self.logger.warning(f"Colonne manquante '{col}' dans {file.name}. Ajout avec des valeurs vides.")
                data[col] = ''

        data = data[cols]
        data = data.replace(np.nan, '', regex=True)
        data = data.astype(str)

        try:
            self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)
            self.logger.info(f"Fichier transformé {file.name} sauvegardé avec succès.")
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la sauvegarde du fichier transformé {file.name}: {e}")

def run_lonasebet_global_transformer():
    transformer = LonasebetGlobalTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_lonasebet_global_transformer()
