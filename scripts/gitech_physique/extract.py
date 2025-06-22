### system ###
import glob
### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date, sleep
from utils.other_utils import move_file, loading
### other ###
from utils.file_manipulation import rename_file
from datetime import timedelta

class ExtractGitechPhysique(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('gitech_physique', env_variables_list, 'logs/extract_gitech_physique.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        usernameId = html_elements["username_element_id"]
        passwordId = html_elements["password_element_id"]
        submit_buttonId = html_elements["login_submit_button_element_id"]
        username = secret_config["GITECH_PHYSIQUE_LOGIN_USERNAME"]
        password = secret_config["GITECH_PHYSIQUE_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        #todo: format
        self.wait_and_send_keys(usernameId, locator_type="id", keys=username, raise_error=True)
        self.wait_and_send_keys(passwordId, locator_type="id", keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_buttonId, locator_type="id")

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, raise_error=True, timeout=10*9)
            self.logger.info("Connexion à la plateforme réussie.")
        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        sleep(10)
        pass

    def _download_files(self):
        start_date = self.start_date
        year = start_date.strftime("%Y")
        self.wait_and_click(f"*//td/a[contains(text(), '{year}')]", locator_type="xpath")
        end_date = self.start_date
        delta = timedelta(days=1)
        sleep(2)
        self._delete_old_files()
        while end_date <= self.end_date:
            day = start_date.strftime("%Y_%m_%d")
            sleep(2)
            for element in self.browser.find_elements(By.XPATH, f"//a[contains(text(), '{day}')]"):
                element.click()
            try:
                self.start_date = start_date
                files_patterns = self.config['files_patterns']
                files_patterns_m = files_patterns.copy()
                for file_pattern in files_patterns:
                    formatted_pattern = file_pattern.replace("*",f"{day}_")
                    try:
                        if self._verify_download(formatted_pattern): files_patterns_m.remove(file_pattern)
                    except Exception as e:
                        self.logger.info(f"Une erreur est survenue lors de la verification du fichier {e}")
                if len(files_patterns_m) > 0:
                    self.logger.warning(f"Certains fichiers n'ont pas été téléchargé {files_patterns_m} ")
                else:
                    self.logger.warning(f"Tous les fichiers ont été téléchargés pour {start_date}")
            except Exception as e:
                self.logger.error(f"Le fichier du {start_date} n'a pas pu être téléchargé, {e}")
                continue
            start_date += delta
            end_date += delta

def run_gitech_physique():
    env_variables_list = ["GITECH_PHYSIQUE_LOGIN_USERNAME", "GITECH_PHYSIQUE_LOGIN_PASSWORD"]
    job = ExtractGitechPhysique(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_gitech_physique()
