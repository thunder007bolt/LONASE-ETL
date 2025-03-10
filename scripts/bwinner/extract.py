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


class ExtractBwinner(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('bwinner', env_variables_list, 'logs/extract_bwinner.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_id = html_elements["login_submit_button_element_id"]
        username = secret_config["BWINNER_LOGIN_USERNAME"]
        password = secret_config["BWINNER_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_xpath, locator_type='xpath', timeout=10*9, keys=username, raise_error=True)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', timeout=10*9, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_id, locator_type='id', timeout=10*9)

        self.logger.info("Vérification de la connexion...")
        try:
            # TODO: Vérifier si la connexion est bien établie
            # verification_xpath = html_elements["verification_xpath"]
            # WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, verification_xpath)))
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
        html_elements = self.config['html_elements']
        browser.get(reports_url)

        self.logger.info("Configuration des paramètres avant la saisie des dates")
        actionone_element_xpath = html_elements['actionone_element_xpath']
        actiontwo_element_xpath = html_elements['actiontwo_element_xpath']
        actionthree_element_xpath = html_elements['actionthree_element_xpath']
        actionfour_element_xpath = html_elements['actionfour_element_xpath']
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.wait_and_click(actionone_element_xpath, locator_type='xpath', timeout=10*9)
        sleep(1)
        self.wait_and_click(actiontwo_element_xpath, locator_type='xpath', timeout=10)
        sleep(1)
        browser.execute_script("window.scrollTo(document.body.scrollHeight,0)")
        self.wait_and_click(actionthree_element_xpath, locator_type='xpath', timeout=10)
        sleep(1)
        self.wait_and_click(actionfour_element_xpath, locator_type='xpath', timeout=10)
        sleep(1)
        self._process_multiple_files()

    def _process_download(self, start_date, end_date):
        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        start_date = start_date.strftime('%d/%m/%Y')
        end_date = end_date.strftime('%d/%m/%Y')
        from_date_element_id = html_elements["from_date_element_id"]
        to_date_element_id = html_elements["to_date_element_id"]
        filter_button_element_id = html_elements["filter_button_element_id"]
        download_button_element_xpath = html_elements["download_button_element_xpath"]

        from_date_element = self.wait_for_click(from_date_element_id, locator_type='id', timeout=15)
        from_date_element.clear()
        from_date_element.send_keys(start_date)
        sleep(1)
        to_date_element = self.wait_for_click(to_date_element_id, locator_type='id', timeout=15)
        to_date_element.clear()
        to_date_element.send_keys(end_date)
        sleep(1)

        self.logger.info("Soumission du formulaire...")
        self.wait_and_click(filter_button_element_id, locator_type='id', timeout=15)
        sleep(2)

        self.logger.info("Télechargement du fichier")
        self.wait_and_click(download_button_element_xpath, locator_type='xpath', timeout=15)

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()

def run_bwinner():
    env_variables_list = ["BWINNER_LOGIN_USERNAME", "BWINNER_LOGIN_PASSWORD"]
    job = ExtractBwinner(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_bwinner()
