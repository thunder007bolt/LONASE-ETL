from pathlib import Path
import numpy as np
import pandas as pd
from base.transformer import Transformer

class EditecLotoTransformer(Transformer):
    def __init__(self):
        super().__init__('editec_loto', 'logs/transformer_editec_loto.log')

    def _transform_file(self, file: Path, date=None):
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            data = pd.read_csv(file, sep=';', index_col=False)

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

        data = pd.DataFrame(data, columns=["AgentLogin", "RetailCategory", "TotalStake", "PaidAmount", "CancelDateTime", "PayableAmount","SettledDateTime", "State", "JOUR", "ANNEE", "MOIS"])
        data["AgentLogin"] = data["AgentLogin"].astype(str).str[-5:]
        data['SettledDateTime'] = pd.to_datetime(data['SettledDateTime'])
        data['CancelDateTime'] = pd.to_datetime(data['CancelDateTime'])


        data = data[
            (data['SettledDateTime'].dt.date == date.date()) |
            (data['CancelDateTime'].dt.date == date.date())
            ]
        data = data.drop(columns=["SettledDateTime","CancelDateTime"])
        data = data.replace(np.nan, '')
        data = data.astype(str)

        self._save_file(file=file, data=data, type="csv", sep=';', encoding='utf8', index=False)

def run_editec_loto_transformer():
    transformer = EditecLotoTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_editec_loto_transformer()
