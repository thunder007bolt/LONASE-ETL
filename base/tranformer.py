from base.logger import Logger
from utils.config_utils import get_config, get_transformation_configurations
from pathlib import Path
from abc import ABC, abstractmethod
from utils.file_manipulation import move_file
import re
import datetime

class Transformer(ABC):
    def __init__(self, name, log_file):
        self.error_file_count = 0
        self.error_file_names_list = []
        self.name = name
        (
            self.config,
            self.base_config,
            self.logger,
            self.transformation_dest_path,
            self.processed_dest_path,
            self.source_path,
            self.file_pattern,
            self.error_dest_path
        ) = get_transformation_configurations(name, log_file)

    def check_error(self):
        if self.error_file_count > 0:
            self.logger.info(f"Certains fichiers n'ont pas été transformé")
            # Todo: Lister les fichiers qui n'ont pas été tranformés

    def set_error(self, filename):
        self.error_file_count += 1
        self.error_file_names_list.append(filename)

    @abstractmethod
    def _transform_file(self, file):
        pass

    def process_transformation(self):
        self.logger.info(f"Transformation des fichiers de {self.source_path} en {self.file_pattern}")
        for file in self.source_path.glob(self.file_pattern):
            self.logger.info(f"Transformation du fichier {file}")
            self._transform_file(file)
        pass

    def set_filename(self, date_str, prefix):
        parts = date_str.split('/')
        if len(parts) == 3:
            csv_filename = f"{prefix} {parts[2]}-{parts[1]}-{parts[0]}.csv"
        else:
            csv_filename = f"{prefix} {date_str}.csv"
        return self.transformation_dest_path / csv_filename

    def _get_file_date(self, file, reverse=False, is_multiple=False):
        if not reverse:
            regex = r"\s*(\d{4}-\d{2}-\d{2})"
            format = "%Y-%m-%d"
        else:
            regex = r"\s*(\d{2}-\d{2}-\d{4})"
            format = "%d-%m-%Y"

        if is_multiple:
            matches = re.findall(regex, file.name)
            dates = [datetime.datetime.strptime(match, format) for match in matches]
            return dates

        match = re.search(regex, file.name)
        date = match.group(1)
        converted_date = datetime.datetime.strptime(date, format)
        return converted_date

    def _build_name(self, file, is_multiple=False, date=None, **kwargs):
        dates = date or self._get_file_date(file, is_multiple=is_multiple, **kwargs)
        if is_multiple:
            return f"{self.name}_transformed_{dates[0].strftime('%Y-%m-%d')}_{dates[1].strftime('%Y-%m-%d')}.csv"
        else:
            return f"{self.name}_transformed_{dates.strftime('%Y-%m-%d')}.csv"

    def _save_file(self, file, data, type="csv",date=None, name=None, reverse=False, is_multiple=False, **kwargs):
        csv_filename = name or self._build_name(file, reverse=reverse, date=date, is_multiple=is_multiple)
        output_file = self.transformation_dest_path / csv_filename
        try:
            if output_file.exists():
                output_file.unlink()
            if type == "csv":
                data.to_csv(output_file, **kwargs)
            elif type == "excel":
                data.to_excel(output_file, **kwargs)

            move_file(file, self.processed_dest_path)
            self.logger.info(f"Le fichier {csv_filename} a été transformé et sauvegardé avec succès.")

        except Exception as e:
            move_file(file, self.error_dest_path)
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la sauvegarde du fichier {csv_filename} : {e}")
            return

    def __del__(self):
        self.logger.info('------------ Ending --------------')