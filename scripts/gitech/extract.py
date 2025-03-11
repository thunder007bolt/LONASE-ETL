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



class ExtractGitech(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('gitech', env_variables_list, 'logs/extract_gitech.log')
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
        username = secret_config["GITECH_LOGIN_USERNAME"]
        password = secret_config["GITECH_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)

        self.logger.info("Envoi du formulaire...")
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, submit_buttonId))).click()

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, verification_xpath)))
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

def run_gitech():
    env_variables_list = ["GITECH_LOGIN_USERNAME", "GITECH_LOGIN_PASSWORD"]
    job = ExtractGitech(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_gitech()
