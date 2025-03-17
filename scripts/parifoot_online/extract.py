### system ###
import glob
### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date, sleep
from utils.other_utils import move_file, loading

class ExtractBwinner(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('parifoot_online', env_variables_list, 'logs/extract_parifoot_online.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_id = html_elements["username_element_id"]
        password_id = html_elements["password_element_id"]
        submit_button_id = html_elements["login_submit_button_element_id"]
        username = secret_config["PARIFOOT_ONLINE_LOGIN_USERNAME"]
        password = secret_config["PARIFOOT_ONLINE_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_id, timeout=10*9, keys=username, raise_error=True)
        self.wait_and_send_keys(password_id, timeout=10*9, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_id, locator_type='id', timeout=10*9)

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
        self._process_multiple_files()
        self.logger.info("Téléchargement des fichiers terminé.")

    def _process_download(self, start_date, end_date):
        self.logger.info("Remplissage des champs de date...")
        #todo: Eviter de recharger la page
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        start_date = start_date.strftime('%d/%m/%Y') + " 00:00"
        end_date = end_date.strftime('%d/%m/%Y') + " 23:59:59"
        self.logger.info("Remplit les champs \"From\" et \"To\"")
        # Remplit les champs "From" et "To"
        self.wait_and_click("tbTo", timeout=50)
        to_field = browser.find_element(By.ID, "tbTo")
        to_field.clear()
        self.wait_and_click("tbFrom", timeout=50)
        from_field = browser.find_element(By.ID, "tbFrom")
        from_field.clear()
        from_field.send_keys(start_date + Keys.ENTER)
        to_field.send_keys(end_date + Keys.ENTER)
        self.logger.info("Ouvre le sélecteur de colonnes et sélectionne celles requises")
        # Ouvre le sélecteur de colonnes et sélectionne celles requises
        required_columns = [
            'ID', 'Balance', 'Total Players', 'Total Players Date Range',
            'SB Wins No.', 'SB Ref No.', 'Cas.Wins No.', 'Cas.Ref No.',
            'Financial Deposits', 'Financial Withdrawals', 'Transaction Fee'
        ]
        self.wait_and_click("//div[@id='tblAgentCasinoAndBettingReport2356671_wrapper']//button[contains(@class, 'ColVis_MasterButton')]", locator_type="xpath")
        checkboxes = browser.find_element(By.XPATH, "//ul[@class='ColVis_collection']").find_elements(By.TAG_NAME, "li")
        for checkbox in checkboxes:
            if checkbox.text in required_columns:
                checkbox.click()

        # Click outside of the zone to validate the selection
        self.wait_and_click("/html/body/div[7]", locator_type="xpath")
        # Clique hors de la zone pour valider la sélection
        #ActionChains(browser).move_by_offset(242, 130).click().perform()
        self.logger.info("Définit la devise")
        #ActionChains(browser).move_by_offset(242, 130).click().perform()
        #ActionChains(browser).move_by_offset(242, 130).click().perform()

        # Définit la devise
        self.wait_and_send_keys("ReportCurrency", keys='West African CFA Franc')
        sleep(3)
        #todo: extraire ces deux fonctions
        def wait_for_condition(condition_func, timeout=120, poll_interval=2):
            """Attend qu'une condition renvoie True ou jusqu'au délai imparti."""
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                if condition_func():
                    return True
                time.sleep(poll_interval)
            return False
        def wait_for_spinner(timeout=120, poll_interval=10):
            """Attend que le spinner de chargement disparaisse."""
            return wait_for_condition(
                lambda: "block" not in browser.find_element(By.CLASS_NAME, "dataTables_processing").get_attribute("style"),
                timeout, poll_interval
            )
        self.logger.info("Attend la fin du chargement")
        # Attend la fin du chargement
        if not wait_for_spinner(timeout=120, poll_interval=10):
            print("Chargement anormalement long, nous allons recommencer")
            self._download_files()
        sleep(3)
        self.logger.info("Applique le filtre")
        # Applique le filtre
        self.wait_and_click("btnFilter", timeout=30)
        if not wait_for_spinner(timeout=120, poll_interval=10):
            print("Chargement anormalement long, nous allons recommencer")
            self._download_files()
        sleep(3)
        self.logger.info("Lance le téléchargement du fichier")
        # Lance le téléchargement du fichier
        self.wait_and_click("ToolTables_tblAgentCasinoAndBettingReport2356671_0")

def run_parifoot_online():
    env_variables_list = ["PARIFOOT_ONLINE_LOGIN_USERNAME", "PARIFOOT_ONLINE_LOGIN_PASSWORD"]
    job = ExtractBwinner(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_parifoot_online()
