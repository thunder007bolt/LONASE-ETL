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
from utils.file_manipulation import rename_file
from datetime import timedelta



class ExtractSolidicon(BaseScrapper):
    def __init__(self, env_variables_list):
        chrome_options_arguments = [
            "--user-data-dir=C:\\Users\\optiware3\\AppData\\Local\\Google\\Chrome\\User Data\\",
            "--profile-directory=Default"
        ]

        super().__init__('solidicon', env_variables_list, 'logs/extract_solidicon.log', chrome_options_arguments=chrome_options_arguments)
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
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["SOLIDICON_LOGIN_USERNAME"]
        password = secret_config["SOLIDICON_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(usernameId, keys=username)
        self.wait_and_send_keys(passwordId, keys=password)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type="xpath")


        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        sleep(10)
        pass

    def _download_files(self):
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        # start_date
        start_date_day_element_id = html_elements["start_date_day_element_id"]
        start_date_month_element_id = html_elements["start_date_month_element_id"]
        start_date_year_element_id = html_elements["start_date_year_element_id"]
        # end_date
        end_date_day_element_id = html_elements["end_date_day_element_id"]
        end_date_month_element_id = html_elements["end_date_month_element_id"]
        end_date_year_element_id = html_elements["end_date_year_element_id"]
        error_message_element_xpath = html_elements["error_message_element_xpath"]

        start_date = self.start_date
        # todo: +1 if include_sup equals true
        end_date = self.start_date
        delta = timedelta(days=1)
        sleep(2)
        while end_date <= self.end_date:
            year, month, day = start_date.strftime("%Y-%m-%d").split("-")
            sleep(2)
            self.fill_select(start_date_day_element_id, value=day)
            self.fill_select(start_date_month_element_id, value=month)
            self.fill_select(start_date_year_element_id, value=year)

            self.fill_select(end_date_day_element_id, value=day)
            self.fill_select(end_date_month_element_id, value=month)
            self.fill_select(end_date_year_element_id, value=year)

            self.logger.info("Soumission du formulaire...")
            submit_button_element_id = html_elements["submit_button_element_id"]
            self.wait_and_click(submit_button_element_id, locator_type='id', timeout=15)

            self.logger.info("Vérification du resultat...")
            try:
                self.wait_for_presence(error_message_element_xpath, locator_type='xpath', timeout=5, raise_error=True)
                self.logger.error(f"Le fichier du {year}-{month}-{day} n'existe pas")
                self._quit()
            except:
                pass

            self.logger.info("Télechargement du fichier")
            download_button_element_id = html_elements["download_button_element_id"]
            self.wait_and_click(download_button_element_id, locator_type='id', timeout=15)

            try:
                self.start_date = start_date
                self._verify_download()
            except:
                self.logger.error(f"Le fichier du {start_date} n'a pas pu être téléchargé, Nous allons recommencer")
                continue

            self.logger.info("Déplacement du fichier...")
            name = f"{self.name}_{start_date.strftime('%Y-%m-%d')}"
            file_pattern = self.config['file_pattern']
            rename_file(file_pattern, self.config["download_path"], name, self.logger)
            start_date += delta
            end_date += delta

def run_solidicon():
    env_variables_list = ["SOLIDICON_LOGIN_USERNAME", "SOLIDICON_LOGIN_PASSWORD"]
    import os
    os.system("taskkill /im chrome.exe /f")
    job = ExtractSolidicon(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_solidicon()
