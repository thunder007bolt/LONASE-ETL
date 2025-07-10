import os
import re
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime
from base.tranformer import  Transformer
from utils.file_manipulation import move_file, check_file_not_empty
import zipfile


class GitechPhysiqueTransformer(Transformer):
    def __init__(self):
        super().__init__('gitech_physique', 'logs/transformer_gitech_physique.log')
        self.zip_path = self.source_path.parent / "zip"
        self.unused_files_path = self.source_path.parent / "unused_files"
        self.others_files_path = self.source_path.parent / "others"

    def _transform_file(self, file: Path, date=None):
        categorie = file.name.split("_")[-1].replace('.csv', '')
        data = pd.read_csv(file, encoding='latin-1', skiprows=1, index_col=False, sep=',')
        data['categorie'] = str(categorie)
        data = pd.DataFrame(data, columns=['TerminalID', 'GameName', 'RaceNo', 'RaceDate', 'SelectedBets',
                                           'BetOption', 'TotalBets', 'BetAmount(CFA.)', 'TransactionDateTime',
                                           'CancelDateTime', 'categorie'])
        regex = r"\s*(\d{4}_\d{2}_\d{2})"
        format = "%Y_%m_%d"
        match = re.search(regex, file.name)
        date = match.group(1)
        converted_date = datetime.strptime(date, format)
        name = f"{self.name}_transformed_{categorie}_{converted_date.strftime('%Y-%m-%d')}.csv"
        self._save_file(file=file, data=data, type="csv", name=name, sep=';', encoding='latin-1', index=False)

    def _extract_zip_files(self):
        zip_files = self.source_path.glob("*.zip")
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.source_path)
            move_file(zip_file, self.zip_path)

    def _move_files(self):
        for file in  self.source_path.glob("*.csv"):
            if any(pat in file.name for pat in ["ALR_Payment"]):
                move_file(file, self.unused_files_path)

        for file in self.source_path.glob("*.csv"):
            if not any(pat in file.name for pat in ["ALR1", "ALR2", "ALR3"]):
                move_file(file, self.others_files_path)

    def process_transformation(self):
        self._extract_zip_files()
        self._move_files()
        self.logger.info(f"Transformation des fichiers de {self.source_path} en {self.file_pattern}")
        for file in self.source_path.glob(self.file_pattern):
            self.logger.info(f"Transformation du fichier {file}")
            if not check_file_not_empty(file): continue
            self._transform_file(file)
        pass


def run_gitech_physique_transformer():
    transformer = GitechPhysiqueTransformer()
    transformer.process_transformation()

if __name__ == '__main__':
    run_gitech_physique_transformer()