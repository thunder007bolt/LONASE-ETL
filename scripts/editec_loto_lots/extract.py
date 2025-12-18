### system ###
import glob
from datetime import timedelta
from sys import base_prefix

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


class ExtractEditecLoto(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('editec_loto_lots', env_variables_list,
                         'logs/extract_editec_loto_lots.log')
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
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["EDITEC_LOTO_LOGIN_USERNAME"]
        password = secret_config["EDITEC_LOTO_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH, username_xpath))).send_keys(
            username)
        WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH, password_xpath))).send_keys(
            password)

        self.logger.info("Envoi du formulaire...")
        WebDriverWait(browser, timeout=10 * 9).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))).click()
        sleep(2)

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            WebDriverWait(browser, timeout=10).until(EC.presence_of_element_located((By.XPATH, verification_xpath)))
            sleep(1)
            self.logger.info("Connexion à la plateforme réussie.")

        except Exception as error:
            self.logger.info("Connexion à la plateforme n'a pas pu être établie.")
            self._quit(error)
    def _manage_dropdown_state(self, desired_state: str, dropdown_ng_select_xpath):


        try:
            wait = WebDriverWait(self.browser, 10)

            dropdown_element = wait.until(
                EC.presence_of_element_located((By.XPATH, dropdown_ng_select_xpath)))

            current_classes = dropdown_element.get_attribute('class')
            is_currently_open = 'ng-select-opened' in current_classes

            action_needed = (desired_state == 'open' and not is_currently_open) or \
                            (desired_state == 'close' and is_currently_open)

            if action_needed:
                self.wait_and_click_v2(dropdown_ng_select_xpath, locator_type="xpath")

                if desired_state == 'open':
                    wait.until(lambda d: 'ng-select-opened' in d.find_element(By.XPATH,
                                                                              dropdown_ng_select_xpath).get_attribute(
                        'class'))
                else:
                    wait.until_not(lambda d: 'ng-select-opened' in d.find_element(By.XPATH,
                                                                                  dropdown_ng_select_xpath).get_attribute(
                        'class'))
            else:
                pass

        except Exception as e:
            self.logger.error(f"Une erreur imprévue est survenue lors de la gestion du dropdown: {e}")
            raise

    def _generate_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        logger.info("Remplissage des champs de date...")

        start_date = self.start_date
        delta = timedelta(days=1)
        end_date = self.start_date + delta
        while end_date <= (self.end_date + delta):
            browser.get(reports_url)
            logger.info("Date début")
            calendar_xpath = html_elements["calendar_xpath"]
            calendar_year_button_xpath = html_elements["calendar_year_button_xpath"]
            calendar_year_xpath = html_elements["calendar_year_xpath"]
            calendar_month_xpath = html_elements["calendar_month_xpath"]
            calendar_day_xpath = html_elements["calendar_day_xpath"]
            search_button_xpath = html_elements["search_button_xpath"]
            report_submit_button_xpath = html_elements["report_submit_button_xpath"]

            self.wait_and_click_v2(calendar_xpath, locator_type="xpath")
            self.wait_and_click_v2(calendar_year_button_xpath, locator_type="xpath")

            # Sélection de la date de début
            for i in browser.find_elements(By.XPATH, calendar_year_xpath):
                if start_date.strftime('%Y') in i.text:
                    i.click()
                    break
            sleep(0.5)
            for i in browser.find_elements(By.XPATH, calendar_month_xpath):
                if start_date.strftime('%b').lower() in i.text.lower():
                    i.click()
                    break
            sleep(0.5)
            for i in browser.find_elements(By.XPATH, calendar_day_xpath):
                if i.text.strip() == start_date.strftime('%d').lstrip('0'):
                    i.click()
                    break
            sleep(0.5)

            # Sélection de la date de fin
            for i in browser.find_elements(By.XPATH, calendar_year_xpath):
                if start_date.strftime('%Y') in i.text:
                    i.click()
                    break
            sleep(0.5)
            for i in browser.find_elements(By.XPATH, calendar_month_xpath):
                if start_date.strftime('%b').lower() in i.text.lower():
                    i.click()
                    break
            sleep(0.5)
            for i in browser.find_elements(By.XPATH, calendar_day_xpath):
                if i.text.strip() == start_date.strftime('%d').lstrip('0'):
                    i.click()
                    break
            sleep(0.5)

            #browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

            self.wait_and_click('/html/body/hg-root/hg-layout/div/div/div', locator_type="xpath")
            self.wait_and_click_v2(search_button_xpath, locator_type="xpath", timeout=10)
            sleep(5)
            self.wait_and_click_v2(report_submit_button_xpath, locator_type="xpath", timeout=10)

            # # XPath racine de la section
            # base_xpath = "/html/body/hg-root/hg-layout/div/div/div/hg-detailed-activity/div/div/hg-agents-detailed-activity/div[2]"
            # base_xpath2 = "/html/body/hg-root/hg-layout/div/div/div/hg-detailed-activity/div/div/hg-agents-detailed-activity/div[3]"
            # temp  = "/html/body/hg-root/hg-layout/div/div/div/hg-detailed-activity/div/div/hg-agents-detailed-activity/div[2]/div[1]/div/div[2]"
            # # Dictionnaire des métriques qu’on veut extraire (clé = nom, valeur = xpath relatif)
            # metrics = {
            #     "Nombre total de paris": f"{base_xpath}/div[1]/div/div[2]",
            #     "Nombre total de tickets": f"{base_xpath}/div[2]/div/div[2]",
            #     "Mises nettes": f"{base_xpath}/div[3]/div/hg-currency/div/span",
            #     "Montant payé": f"{base_xpath}/div[4]/div/hg-currency/div/span",
            #     "Montant remboursé payé": f"{base_xpath}/div[5]/div/hg-currency/div/span",
            #     "Montant gagné payé": f"{base_xpath}/div[6]/div/hg-currency/div/span",
            #     "Mises en cours": f"{base_xpath}/div[7]/div/hg-currency/div/span",
            #
            #     "Nombre total de tickets annulés": f"{base_xpath2}/div[1]/div/div[2]",
            #     "Taux d'annulation des tickets": f"{base_xpath2}/div[2]/div/div[2]",
            #     "Montant des mises annulées": f"{base_xpath2}/div[3]/div/hg-currency/div/span",
            #     "Taux de mises annulées": f"{base_xpath2}/div[4]/div/div[2]",
            #     "Montant des corrections": f"{base_xpath2}/div[5]/div/hg-currency/div/span",
            #     "Delta balance": f"{base_xpath2}/div[6]/div/hg-currency/div/span",
            #     "Montant Payable": f"{base_xpath2}/div[7]/div/hg-currency/div/span",
            #     "Montant des dépôts clients": f"{base_xpath2}/div[8]/div/hg-currency/div/span",
            #     "Montant des retraits clients": f"{base_xpath2}/div[9]/div/hg-currency/div/span",
            # }
            #
            # results = {}
            # for key, xpath in metrics.items():
            #     try:
            #         element = self.wait_for_presence(xpath, locator_type="xpath")
            #         value = element.text.strip()
            #
            #         # transformation en snake_case sans accents
            #         import re
            #         from unidecode import unidecode
            #         key_snake = re.sub(r"[^\w\s]", "", unidecode(key)).lower().replace(" ", "_")
            #
            #         results[key_snake] = value
            #     except Exception as e:
            #         logger.error(f"Impossible de récupérer {key}: {e}")
            #         results[key_snake] = None
            #
            # sleep(5)
            #
            # # Transformation en DataFrame
            # import pandas as pd
            # df = pd.DataFrame([results])
            # df["JOUR"] = str(start_date.strftime("%d/%m/%Y"))
            # df["ANNEE"] = str(start_date.strftime("%Y"))
            # df["MOIS"] = str(start_date.strftime("%m"))
            # self.logger.info(f"DataFrame final : {start_date}")
            # filename = f"editec_loto_lots_transformed_{start_date}.csv"
            # full_path = self.transformation_dest_path / filename
            # df.to_csv(full_path, index=False, sep=";", encoding="utf-8")
            self.logger.info(f"{start_date} Generated")
            start_date += delta
            end_date += delta

    def _download_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        url = self.config['urls']['report_history']

        table_xpath = html_elements['table_xpath']
        table_row_xpath = html_elements['table_row_xpath']
        download_button_xpath = html_elements['download_button_xpath']

        self.logger.info("Chargement de la page historique des rapports...")
        retry_operation(self, operation=lambda: browser.get(url))
        self.wait_for_presence(table_xpath, timeout=20)
        self.wait_for_presence(table_row_xpath, timeout=20)
        rows = browser.find_elements(by=By.XPATH, value=table_row_xpath)
        start_date = self.start_date
        delta = timedelta(days=1)
        end_date = self.start_date + delta
        while end_date <= (self.end_date + delta):
            for row in rows:
                start_date_formated = (start_date).strftime('%d/%m/%Y')
                end_date_formated = (start_date ).strftime('%d/%m/%Y')
                columns = row.find_elements(by=By.TAG_NAME, value="td")
                if len(columns) < 5:
                    continue
                logger.info(f"Report name: {columns[1].text}, Dates: {columns[2].text}, {columns[3].text}, Status: {columns[4].text}")
                report_name = columns[2].text
                type = columns[3].text
                date1 = columns[4].text
                date2 = columns[5].text
                status = columns[6].text
                founded_file_name = "TreasuryCashManagement" in report_name and \
                                    type == 'XLSX' and \
                                    date1 == start_date_formated and \
                                    date2 == end_date_formated

                if founded_file_name and "Disponible" in status:
                    logger.info("Téléchargement du fichier...")
                    download_button = row.find_element(by=By.XPATH, value=download_button_xpath)
                    # self.wait_and_click(download_button, locator_type="xpath")
                    WebDriverWait(row, timeout=10).until(EC.element_to_be_clickable(download_button)).click()
                    logger.info("Téléchargement lancé avec succès.")
                    try:
                        self.start_date = start_date
                        self._verify_download()
                        name = f"{self.name}_{start_date.strftime('%Y-%m-%d')}"
                        file_pattern = self.config['file_pattern']
                        rename_file(file_pattern, self.config["download_path"], name, self.logger)
                        if (end_date == (self.end_date + delta) or self.start_date == self.end_date):
                            self.logger.info("Tous les fichiers ont été téléchargés")
                            #todo: fin propre du fichier
                            break
                        continue
                    except:
                        self.logger.error(
                            f"Le fichier du {start_date} n'a pas pu être téléchargé")

                elif founded_file_name and (status in ["En attente", "En cours de traitement"]):
                    self.logger.info(f"Le fichier du {start_date} est en attente de téléchargement")
                    sleep(10)
                    self.logger.info("Rétéléchargement du fichier")
                    self._download_files()
                    return

                else:
                    self.logger.error(f"Le fichier du {start_date} n'a pas pu être téléchargé")
                    continue
            start_date += delta
            end_date += delta
    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._generate_files()
        """
        def generate_date_range(start_date, end_date):
              return [{"start_date": start_date + timedelta(days=i),
                       "end_date": start_date + timedelta(days=i)}
                      for i in range((end_date - start_date).days + 1)]

        self.files = generate_date_range(self.start_date, self.end_date)
        #"""
        self._download_files()

def run_editec_loto_lots():
    env_variables_list = ["EDITEC_LOTO_LOGIN_USERNAME", "EDITEC_LOTO_LOGIN_PASSWORD"]
    job = ExtractEditecLoto(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_editec_loto_lots()
