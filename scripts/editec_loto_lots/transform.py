from pathlib import Path
import numpy as np
import pandas as pd
from base.tranformer import Transformer

class EditecLotoTransformer(Transformer):
    def __init__(self):
        super().__init__('editec_loto_lots', 'logs/transformer_editec_loto_lots.log')

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            data = pd.read_excel(file, sheet_name='Data')

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        date = self._get_file_date(file)
        data["JOUR"] = str(date.strftime("%d/%m/%Y"))
        data["ANNEE"] = str(date.strftime("%Y"))
        data["MOIS"] = str(date.strftime("%m"))

        # filesInitialDirectory = r"K:\DATA_FICHIERS\LONASEBET\CASINO\\"
        # data.to_csv(filesInitialDirectory + "casinoLonasebet "+ date.strftime('%Y-%m-%d') + ".csv", index=False,sep=';',encoding='utf8')

        data = pd.DataFrame(data, columns=["AgentLogin", "RetailCategory", "TotalDrawGamePaidAmount", "JOUR", "ANNEE", "MOIS"])
        data["AgentLogin"] = data["AgentLogin"].astype(str).str[-5:]


        data = data.replace(np.nan, '')
        data = data.astype(str)

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)

def run_editec_loto_lots_transformer():
    transformer = EditecLotoTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_editec_loto_lots_transformer()
