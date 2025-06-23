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

        data = data.replace(np.nan, '', regex=True)
        data = data.astype(str)

        try:
            self._save_file(file=file, data=data, type="csv", sep=';', encoding='latin1', index=False)
            self.logger.info(f"Fichier transformé {file.name} sauvegardé avec succès.")
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la sauvegarde du fichier transformé {file.name}: {e}")

def run_lonasebet_global_transformer():
    transformer = LonasebetGlobalTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_lonasebet_global_transformer()
