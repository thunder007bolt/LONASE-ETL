import os
import re
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import win32com.client
from datetime import datetime
from base.logger import Logger
from base.tranformer import Transformer
from utils.config_utils import get_config
from utils.file_manipulation import move_file


class AfitechDailyPaymentActivityTransformer(Transformer):
    def __init__(self):
        super().__init__('afitech_betting_operation', 'logs/transformer_afitech_betting_operation.log')

    def _transform_file(self, file: Path, date=None):
        """
        """
        self.logger.info(f"Traitement du fichier : {file.name}")

        try:
            # Ouvrir le fichier Excel et s'assurer qu'il est fermé après lecture
            with pd.ExcelFile(file) as xl:
                available_sheets = xl.sheet_names

                # Feuilles attendues
                expected_sheets = ["Data", "Data2", "Data3"]

                # Charger uniquement celles qui existent
                dfs = []
                for sheet in expected_sheets:
                    if sheet in available_sheets:
                        df = xl.parse(sheet)
                        dfs.append(df)

            if not dfs:  # Aucun DataFrame trouvé
                self.set_error(file.name)
                self.logger.error(f"Aucune feuille trouvée dans {file.name}")
                return

            # Concaténer toutes les feuilles
            data = pd.concat(dfs, ignore_index=True)

        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            return

        # Renommer les colonnes
        data = data.rename(columns={
            "Date Time": "date_time",
            "Betting Operation Ref": "betting_operation_ref",
            "Operator": "operator",
            "Game Type": "game_type",
            "State": "state",
            "Stake": "stake",
            "Paid Amount": "paid_amount"
        })

        # Garder uniquement les colonnes nécessaires
        data = data[[
            "date_time",
            "betting_operation_ref",
            "operator",
            "game_type",
            "state",
            "stake",
            "paid_amount"
        ]]
        data['paid_amount'] = pd.to_numeric(data['paid_amount'].replace('-', '0'), errors='coerce').fillna(0)
        data['stake'] = pd.to_numeric(data['stake'].replace('-', '0'), errors='coerce').fillna(0)
        # Convertir en string
        data = data.astype(str)

        # Sauvegarde finale
        self._save_file(file, data, type="csv", index=False, sep=';', encoding='utf8', reverse=True)


def run_afitech_betting_operation_transformer():
    transformer = AfitechDailyPaymentActivityTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_afitech_betting_operation_transformer()
