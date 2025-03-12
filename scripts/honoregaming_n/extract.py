### system ###
import glob

from base.ftp import BaseFTP
from utils.date_utils import get_yesterday_date
import datetime

class ExtractHonoreGaming(BaseFTP):
    def __init__(self, env_variables_list):
        super().__init__('honore_gaming', 'logs/extract_honore_gaming.log', env_variables_list)
        self.file_path = None

    def _setup_files_pattern(self):
        if self.date:
            self.files_pattern = f"'daily-modified-horse-racing-tickets-detailed_'{self.date}.csv"
        else:
            self.date = datetime.date.today().strftime("%Y%m%d")
            self.files_pattern = f"daily-modified-horse-racing-tickets-detailed_{self.date}.csv"

    def process_extraction(self):
        self._setup_files_pattern()
        self._login()
        self._download_files()
        self._verify_download()

def run_honore_gaming():
    env_variables_list = ["FTP_HOST", "FTP_USERNAME", "FTP_PASSWORD"]
    job = ExtractHonoreGaming(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_honore_gaming()
