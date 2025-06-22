### system ###
import glob

from base.ftp import BaseFTP
from utils.date_utils import get_yesterday_date
import datetime
from utils.file_manipulation import copy_files

class ExtractHonoreGaming(BaseFTP):
    def __init__(self, env_variables_list):
        super().__init__('honore_gaming', 'logs/extract_honore_gaming.log', env_variables_list)
        self.file_path = None

    def process_extraction(self):
        self._login()
        self._download_files()
        self._verify_download()
        ### Todo: A supprimer
        path = r"K:\DATA_FICHIERS\HONORE_GAMING\\"
        copy_files(self.file_pattern, self.extraction_dest_relative_path, path , self.logger)
        ###
        self.rename_file()



def run_honore_gaming():
    env_variables_list = ["FTP_HOST", "FTP_USERNAME", "FTP_PASSWORD"]
    job = ExtractHonoreGaming(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_honore_gaming()
