### system ###
import glob
from datetime import timedelta
import calendar, datetime

import pyotp

### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date, sleep
from utils.other_utils import move_file, loading, retry_operation
from utils.file_manipulation import rename_file

from selenium.common.exceptions import StaleElementReferenceException


class ExtractAfitechCommissionHistory(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('afitech_commission_history', env_variables_list,
                         'logs/extract_afitech_commission_history.log')
        self.file_path = None
        self.range = False
        self.files = []

    def _set_date(self):
        _, _, _, yesterday_date = get_yesterday_date()
        if self.config["start_date"] is not None:
            self.range = True
            self.start_date = self.config["start_date"]
        else:
            self.start_date = None

        if self.config["end_date"] is not None:
            self.end_date = self.config["end_date"]
        else:
            self.end_date = yesterday_date

        pass

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["AFITECH_LOGIN_USERNAME"]
        password = secret_config["AFITECH_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_xpath, keys=username, locator_type="xpath")
        self.wait_and_send_keys(password_xpath, keys=password, locator_type="xpath")

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type="xpath")

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")
        except Exception as error:
            self.logger.info("Connexion à la plateforme n'a pas pu être établie.")
            self._quit(error)

        try:
            self.logger.info("Authentification...")
            dropdown_element_xpath = html_elements["dropdown_element_xpath"]
            google_authentication_element_xpath = html_elements["google_authentication_element_xpath"]
            code_input_element_xpath = html_elements["code_input_element_xpath"]
            opt_url = self.secret_config["AFITECH_GET_OTP_URL"]

            self.logger.info("Choix de la méthode d'authentification...")
            self.wait_and_click(dropdown_element_xpath, locator_type="xpath")
            self.wait_and_click(google_authentication_element_xpath, locator_type="xpath")

            self.logger.info("Récupération du code...")
            code = pyotp.parse_uri(opt_url).now()

            self.logger.info("Saisie du code de confirmation...")
            self.wait_and_send_keys(code_input_element_xpath, keys=code, locator_type="xpath")

        except Exception as error:
            self.logger.error("Authentification n'a pas pu être effectuée.")
            self._quit(error)

        try:
            self.logger.info("Verification du la page de rapports...")
            report_verification_xpath = html_elements["report_verification_xpath"]
            self.wait_for_presence(report_verification_xpath, timeout=15, raise_error=True)
            self.logger.info("Connexion à la plateforme réussie.")

        except Exception as error:

            self._connection_to_platform()
            self.logger.error("La page de rapports n'a pas pu être chargée.")
            self._quit(error)

    def _generate_files(self):

        delta = timedelta(days=1)
        if self.range:
            end_date = self.start_date
        else:
            end_date = self.end_date
        while end_date <= (self.end_date):
            current_date = end_date
            start_date = datetime.date((current_date).year, (current_date).month, 1)
            start_date_formated = start_date.strftime('%d/%m/%Y')
            end_date_formated = (current_date).strftime('%d/%m/%Y')

            browser = self.browser
            html_elements = self.config['html_elements']
            logger = self.logger

            logger.info("Chargement de la page des rapports...")
            reports_url = self.config['urls']['report']
            browser.get(reports_url)

            logger.info("Sélection du rapport...")
            report_dropdown_xpath = html_elements["report_dropdown_xpath"]
            report_type_xpath = html_elements["report_type_xpath"]
            self.wait_and_click(report_dropdown_xpath, locator_type="xpath")
            self.wait_and_click(report_type_xpath, locator_type="xpath")

            start_calendar_input_xpath = html_elements["start_calendar_input_xpath"]
            end_calendar_input_xpath = html_elements["end_calendar_input_xpath"]

            start_calendar_input = browser.find_element(by=By.XPATH, value=start_calendar_input_xpath)
            start_calendar_input.send_keys(start_date_formated + Keys.ENTER)
            end_calendar_input = browser.find_element(by=By.XPATH, value=end_calendar_input_xpath)
            end_calendar_input.send_keys(end_date_formated + Keys.ENTER)

            logger.info("Soumission du formulaire...")
            report_submit_button_xpath = html_elements["report_submit_button_xpath"]
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

            self.wait_and_click(report_submit_button_xpath, locator_type="xpath")

            try:
                libelle = 'Report created successfully'
                self.wait_for_presence("//div[contains(text(),'" + libelle + "')]", timeout=10 * 9)
                self.files.append({"start_date": start_date, "end_date": end_date})
                logger.info(
                    f"Le fichier CommissionHistory de la plateforme AFITECH  du {start_date}  au {end_date} a bien ete genere")

            except Exception as error:
                logger.error(
                    f"Le fichier CommissionHistory de la plateforme AFITECH  du {start_date} au {end_date} n'a pas pu ete genere")
                self._quit(error)
            end_date += delta

    def _download_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger
        url = self.config['urls']['report_history']
        table_xpath = html_elements['table_xpath']
        table_row_xpath = html_elements['table_row_xpath']
        download_button_xpath = html_elements['download_button_xpath']



        while self.files:
            logger.info("Chargement de la page historique des rapports...")
            browser.get(url)  # Reload the page to get fresh elements

            # Wait for the table and other elements to load
            self.wait_for_presence(table_xpath)
            self.wait_for_presence(
                "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button",
            )
            self.wait_and_click(
                "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button",
                locator_type="xpath")
            self.wait_and_click(
                "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button",
                locator_type="xpath")
            self.wait_and_click(
                "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button",
                locator_type="xpath")
            self.wait_and_click(
                "/html/body/hg-root/hg-layout/div/div/div/hg-report-history/div/div[3]/div/p-tabview/div/div[2]/p-tabpanel[1]/div/hg-load-more/div/hg-button/button",
                locator_type="xpath")
            # Process rows with fresh elements each iteration
            # Process rows with fresh elements each iteration
            rows = browser.find_elements(by=By.XPATH, value=table_row_xpath)

            for row in rows:
                try:
                    columns = row.find_elements(by=By.TAG_NAME, value="td")
                    if len(columns) < 5:
                        continue
                    report_name = columns[1].text
                    date1 = columns[2].text
                    date2 = columns[3].text
                    status = columns[4].text

                    # Check if the row matches a file in self.files
                    founded = False
                    idx = None
                    formated_start_date = ""
                    formated_end_date = ""
                    for index, file in enumerate(self.files):
                        formated_start_date = file["start_date"].strftime('%d/%m/%Y')
                        formated_end_date = file["end_date"].strftime('%d/%m/%Y')
                        if (formated_start_date in date1 and formated_end_date in date2):
                            founded = True
                            idx = index
                            break

                    founded_file_name = "CommissionHistory" in report_name and founded
                    if founded_file_name and "Available" in status:
                        logger.info("Téléchargement du fichier...")
                        download_button = row.find_element(by=By.XPATH, value=download_button_xpath)
                        WebDriverWait(row, timeout=10).until(EC.element_to_be_clickable(download_button)).click()
                        logger.info("Téléchargement lancé avec succès.")
                        try:
                            self._verify_download()
                            name = f"{self.name}_{formated_start_date.replace('/', '-')}_{formated_end_date.replace('/', '-')}"
                            file_pattern = self.config['file_pattern']
                            rename_file(file_pattern, self.config["download_path"], name, logger)
                            del self.files[idx]  # Remove downloaded file from list
                        except Exception as e:
                            logger.error(f"Le fichier du {date1} n'a pas pu être téléchargé: {str(e)}")

                    elif founded_file_name and status in ["Incomplete", "Queued", "In Progress"]:
                        logger.info(f"Le fichier du {date1} est en attente de téléchargement")
                except Exception as e:
                    logger.info(f"Erreur {e}")



    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._generate_files()
        """
        def generate_date_range(start_date, end_date):
            return [{"start_date": start_date,
                     "end_date": start_date + timedelta(days=i)}
                    for i in range((end_date - start_date).days + 1)]

        self.files = generate_date_range(self.start_date, self.end_date)
        """
        self._download_files()

def run_afitech_commission_history():
    env_variables_list = ["AFITECH_LOGIN_USERNAME", "AFITECH_LOGIN_PASSWORD", "AFITECH_GET_OTP_URL"]
    job = ExtractAfitechCommissionHistory(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_afitech_commission_history()
