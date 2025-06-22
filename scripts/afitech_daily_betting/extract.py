### system ###
import glob
from datetime import timedelta

### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

### utils ###
from utils.date_utils import sleep
from utils.file_manipulation import rename_file2

import pyotp


class ExtractAfitechDailyBetting(BaseScrapper):
    def __init__(self, env_variables_list, start_date=None, end_date=None):
        super().__init__(
            name='afitech_daily_betting',
            env_variables_list=env_variables_list,
            log_file='logs/extract_afitech_daily_betting.log',
            start_date=start_date,
            end_date=end_date
        )
        self.file_path = None
        self.range = False
        self.files = []
        self.retry = 0

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

        attempts = 3
        for attempt in range(0, attempts):
            try:
                self.logger.info("Saisie des identifiants...")
                self.wait_and_send_keys(username_xpath, keys=username, locator_type="xpath", raise_error=True)
                self.wait_and_send_keys(password_xpath, keys=password, locator_type="xpath", raise_error=True)

                self.logger.info("Envoi du formulaire...")
                self.wait_and_click(submit_button_xpath, locator_type="xpath", raise_error=True)

                is_connected = self._dashboard_page_verification()

                if is_connected:
                    return True
                else:
                    self.logger.info("Vérification de la connexion...")
                    verification_xpath = html_elements["verification_xpath"]
                    self.wait_for_presence(verification_xpath, raise_error=True)

                    self.logger.info("Authentification...")
                    dropdown_element_xpath = html_elements["dropdown_element_xpath"]
                    google_authentication_element_xpath = html_elements["google_authentication_element_xpath"]
                    code_input_element_xpath = html_elements["code_input_element_xpath"]
                    opt_url = self.secret_config["AFITECH_GET_OTP_URL"]

                    self.logger.info("Choix de la méthode d'authentification...")
                    self.wait_and_click(dropdown_element_xpath, locator_type="xpath", raise_error=True)
                    self.wait_and_click(google_authentication_element_xpath, locator_type="xpath", raise_error=True)

                    self.logger.info("Récupération du code...")
                    code = pyotp.parse_uri(opt_url).now()

                    self.logger.info("Saisie du code de confirmation...")
                    self.wait_and_send_keys(code_input_element_xpath, keys=code, locator_type="xpath", raise_error=True)

                    self.logger.info("Verification du la page de rapports...")
                    report_verification_xpath = html_elements["report_verification_xpath"]
                    self.wait_for_presence(report_verification_xpath, timeout=15, raise_error=True)
                    self.logger.info("Connexion à la plateforme réussie.")
                    break

            except Exception as e:
                self.logger.info(f"Tentative de connexion {attempt}")
                if attempt == attempts:
                    raise e

    def _report_page_verificaton(self):
        html_elements = self.config['html_elements']
        self.logger.info("Verification du la page de rapports...")
        report_dropdown_xpath = html_elements["report_dropdown_xpath"]
        try:
            self.wait_for_presence(report_dropdown_xpath, timeout=120, raise_error=True)
            self.logger.info("Connexion à la plateforme réussie.")
            return True
        except Exception as e:
            self.logger.info("Connexion a echoué")
            return False

    def _dashboard_page_verification(self):
        html_elements = self.config['html_elements']
        self.logger.info("Verification du la page de rapports...")
        report_verification_xpath = html_elements["report_verification_xpath"]
        try:
            self.wait_for_presence(report_verification_xpath, timeout=120, raise_error=True)
            self.logger.info("Connexion à la plateforme réussie.")
            return True
        except Exception as e:
            self.logger.info("Connexion a echoué")
            return False

    def _generate_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']

        start_date = self.start_date
        delta = timedelta(days=1)
        end_date = self.start_date
        browser.get(reports_url)
        while end_date <= (self.end_date):
            for index, file in enumerate(self.files):
                formated_start_date = file["start_date"]
                formated_end_date = file["end_date"]
                if (formated_start_date == end_date and formated_end_date == end_date):
                    start_date += delta
                    end_date += delta
                    continue

            logger.info("Sélection du rapport...")
            report_dropdown_xpath = html_elements["report_dropdown_xpath"]
            report_type_xpath = html_elements["report_type_xpath"]

            try:
                self.wait_and_click(report_dropdown_xpath, locator_type="xpath", raise_error=True)
                self.wait_and_click(report_type_xpath, locator_type="xpath", raise_error=True)
                logger.info("Remplissage des champs de date...")
                start_date_formated = f"{start_date.strftime('%d/%m/%Y')}"
                end_date_formated = f"{start_date.strftime('%d/%m/%Y')}"

                start_calendar_input_xpath = html_elements["start_calendar_input_xpath"]
                end_calendar_input_xpath = html_elements["end_calendar_input_xpath"]

                self.wait_for_presence(start_calendar_input_xpath, raise_error=True)
                start_calendar_input = browser.find_element(by=By.XPATH, value=start_calendar_input_xpath)
                start_calendar_input.send_keys(start_date_formated + Keys.ENTER)
                self.wait_for_presence(end_calendar_input_xpath, raise_error=True)
                end_calendar_input = browser.find_element(by=By.XPATH, value=end_calendar_input_xpath)
                end_calendar_input.send_keys(end_date_formated + Keys.ENTER)
                sleep(1)
                logger.info("Soumission du formulaire...")
                report_submit_button_xpath = html_elements["report_submit_button_xpath"]
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                self.wait_and_click(report_submit_button_xpath, locator_type="xpath", timeout=10, raise_error=True)

            except Exception as e:
                if self.retry == 3 :
                    raise e
                else:
                    is_connected = self._dashboard_page_verification() or self._report_page_verificaton()
                    if is_connected:
                        browser.get(reports_url)
                        continue
                    self._connection_to_platform()
                self.retry = self.retry + 1
                continue

            self.retry = 0
            try:
                libelle = 'Report created successfully'
                pattern = "//div[contains(text(),'" + libelle + "')]"
                self.wait_for_presence(pattern, timeout=15, raise_error=True)
                self.files.append({"start_date": start_date, "end_date": end_date})
                self.wait_for_invisibility(pattern)
                logger.info(
                    f"Le fichier DAILY BETTING de la plateforme AFITECH  du {start_date} a bien ete genere")

            except Exception as error:
                logger.error(
                    f"Le fichier DAILY BETTING de la plateforme AFITECH  du {start_date} au {end_date} n'a pas pu ete genere {error}")
                sleep(60*5)
                continue
                #self.files_with_error.append({"start_date": start_date, "end_date": end_date})
            start_date += delta
            end_date += delta

    def _check_and_clean_download_directory(self):

        files = list(self.extraction_dest_path.glob("*DailyBetting*xlsx"))
        if files:
            self.logger.warning(
                f"Fichiers résiduels trouvés dans {self.extraction_dest_path}: {[f.name for f in files]}")
            sleep(15)
            for file in files:
                try:
                    file.unlink()
                    self.logger.info(f"Fichier résiduel {file.name} supprimé.")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la suppression de {file.name}: {e}")
                    raise
        else:
            self.logger.info(f"Aucun fichier résiduel trouvé dans {self.extraction_dest_path}.")

    def _download2(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger
        url = self.config['urls']['report_history']
        table_xpath = html_elements['table_xpath']
        table_row_xpath = html_elements['table_row_xpath']
        more_button_xpath = html_elements['more_button_xpath']

        while self.files:
            logger.info("Chargement de la page historique des rapports...")
            browser.get(url)

            self.wait_for_presence(table_xpath, timeout=40)
            self.wait_for_presence( more_button_xpath, timeout=40)
            page_number = self.config["page_number"]
            for i in range(0, page_number):
                self.wait_and_click(more_button_xpath, locator_type="xpath")

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

                    founded_file_name = "DailyBetting" in report_name and founded
                    if founded_file_name and "Available" in status:
                        logger.info("Téléchargement du fichier...")
                        try:

                            self._check_and_clean_download_directory()
                            download_button = row.find_element(By.XPATH, "./td[6]//span[@class='icon pointer']")
                            WebDriverWait(browser, 30).until(
                                EC.element_to_be_clickable(download_button)
                            )
                            browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                                                  download_button)
                            sleep(1)
                            download_button.click()

                        except Exception as e:
                            self.logger.info(f"Erreur lors du clic normal on réésaie avec le js {e}")
                            raise e
                        try:
                            founded_file = self._verify_download_v2()
                            sleep(2)
                            name = f"{self.name}_{formated_start_date.replace('/', '-')}_{formated_end_date.replace('/', '-')}"
                            rename_file2(founded_file, self.config["download_path"], name, logger)
                            del self.files[idx]  # Remove downloaded file from list
                        except Exception as e:
                            logger.error(f"Le fichier du {date1} n'a pas pu être téléchargé: {str(e)}")

                    elif founded_file_name and status in ["Incomplete", "Queued", "In Progress"]:
                        logger.info(f"Le fichier du {date1} est en attente de téléchargement")
                except Exception as e:
                    logger.info(f"Erreur {e}")

        self.logger.info("Operation terminé")
        return True

    def _download_files(self):
       pass

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._generate_files()
        #self._download_files()
        """
        def generate_date_range(start_date, end_date):
           return [{"start_date": start_date + timedelta(days=i),
                    "end_date": start_date + timedelta(days=i)}
                   for i in range((end_date - start_date).days + 1)]

        self.files = generate_date_range(self.start_date, self.end_date)
        #"""
        self._download2()


def run_afitech_daily_betting_activity():
    env_variables_list = ["AFITECH_LOGIN_USERNAME", "AFITECH_LOGIN_PASSWORD", "AFITECH_GET_OTP_URL"]
    job = ExtractAfitechDailyBetting(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_afitech_daily_betting_activity()
