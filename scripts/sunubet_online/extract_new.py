### system ###
import glob
from datetime import timedelta, datetime
from pathlib import Path

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


class ExtractSunubetOnline(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('sunubet_online', env_variables_list,
                         'logs/extract_sunubet_online.log')
        self.file_path = None
        self.files = []
        self.regeneration_count = 0

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
        username = secret_config["SUNUBET_CASINO_LOGIN_USERNAME"]
        password = secret_config["SUNUBET_CASINO_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_xpath, keys=username, locator_type="xpath")
        self.wait_and_send_keys(password_xpath, keys=password, locator_type="xpath")

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type="xpath")
        sleep(2)

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
            sleep(1)
            self.logger.info("Connexion à la plateforme réussie.")
        except Exception as error:
            self.logger.info("Connexion à la plateforme n'a pas pu être établie.")
            self._quit(error)

    def _generate_file(self, start_date, end_date, reports_url, browser, logger, html_elements):
        browser.get(reports_url)
        logger.info("Date début")
        calendar_start_xpath = html_elements["calendar_start_xpath"]
        calendar_start_button_xpath = html_elements["calendar_start_button_xpath"]
        calendar_start_month_year_xpath = html_elements["calendar_start_month_year_xpath"]
        calendar_start_day_xpath = html_elements["calendar_start_day_xpath"]

        self.wait_and_click(
            "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[1]/div[2]/div/hg-create-report-button[4]/button",
            locator_type="xpath")
        self.wait_and_click("/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/button",
                            locator_type="xpath")
        self.wait_and_click(
            "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[1]/div/button[2]",
            locator_type="xpath")
        sleep(1)
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(1)

        self.wait_and_click(calendar_start_xpath, locator_type="xpath")
        self.wait_and_click(calendar_start_button_xpath, locator_type="xpath")

        for i in browser.find_elements(by=By.XPATH, value=calendar_start_month_year_xpath):
            if start_date.strftime('%Y') in i.text:
                i.click()
                break
        sleep(1)
        for i in browser.find_elements(by=By.XPATH, value=calendar_start_month_year_xpath):
            if start_date.strftime('%b') in i.text:
                i.click()
                break
        sleep(1)
        for i in browser.find_elements(by=By.XPATH, value=calendar_start_day_xpath):
            if (str(0) + i.text.strip())[-2:] in start_date.strftime('%d'):
                i.click()
                break
        sleep(1)

        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(1)

        logger.info("Date fin")
        calendar_end_xpath = html_elements["calendar_end_xpath"]
        calendar_end_month_year_xpath = html_elements["calendar_end_month_year_xpath"]
        calendar_end_day_xpath = html_elements["calendar_end_day_xpath"]
        self.wait_and_click(calendar_end_xpath, locator_type="xpath")
        self.wait_and_click(
            "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/div[3]/button[1]",
            locator_type="xpath")
        self.wait_and_click(
            "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[2]/div[1]/button[1]",
            locator_type="xpath")
        self.wait_and_click(
            "/html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[5]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]",
            locator_type="xpath")
        for i in browser.find_elements(by=By.XPATH, value=calendar_end_month_year_xpath):
            if end_date.strftime('%Y') in i.text:
                i.click()
                break
        sleep(1)
        for i in browser.find_elements(by=By.XPATH, value=calendar_end_month_year_xpath):
            if end_date.strftime('%b') in i.text:
                i.click()
                break
        sleep(1)
        for i in browser.find_elements(by=By.XPATH, value=calendar_end_day_xpath):
            if (str(0) + i.text.strip())[-2:] in end_date.strftime('%d'):
                i.click()
                break
        sleep(1)

        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(1)

        logger.info("Soumission du formulaire...")
        submit_button_xpath = html_elements["report_submit_button_xpath"]
        self.wait_and_click(submit_button_xpath, locator_type="xpath")
        sleep(5)
        # todo verifié si le fichier a bient été générer dans le cas contaire ne pas incrémenter les dates
        self.files.append({"start_date": start_date, "end_date": end_date})
        pass

    def _regenerate_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        logger.info("Remplissage des champs de date...")

        if len(self.files) > 0:
            error_files = self.files.copy()
            self.files.clear()
            for row in error_files:
                self._generate_file(row['start_date'], row['end_date'], reports_url, browser, logger, html_elements)

        self._download_files()
        pass

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
            self._generate_file(start_date, end_date, reports_url, browser, logger, html_elements)

            start_date += delta
            end_date += delta

    def _download_files(self):
        browser = self.browser
        html_elements = self.config['html_elements']
        logger = self.logger

        url = self.config['urls']['report_history']

        self.logger.info("Chargement de la page historique des rapports...")
        retry_operation(self, operation=lambda: browser.get(url))
        depth = 3
        for index in range(depth):
            url = self.config['urls']['report_history'] + f"?pageIndex={index + 1}"

            table_xpath = html_elements['table_xpath']
            table_row_xpath = html_elements['table_row_xpath']
            download_button_xpath = html_elements['download_button_xpath']

            self.logger.info("Chargement de la page historique des rapports...")
            retry_operation(self, operation=lambda: browser.get(url))

            self.wait_for_presence(table_xpath, timeout=60 * 3)
            self.wait_for_presence(table_row_xpath, timeout=60 * 3)
            rows = browser.find_elements(by=By.XPATH, value=table_row_xpath)
            for row in rows:
                columns = row.find_elements(by=By.TAG_NAME, value="td")
                if len(columns) < 5:
                    continue
                logger.info(
                    f"Report name: {columns[1].text}, Dates: {columns[4].text}, {columns[5].text}, Status: {columns[6].text}")
                report_name = columns[2].text
                type = columns[3].text
                date1 = columns[4].text
                date2 = columns[5].text
                date1_formated = datetime.strptime(date1, "%d/%m/%Y").strftime("%Y-%m-%d")
                date2_formated = datetime.strptime(date2, "%d/%m/%Y").strftime("%Y-%m-%d")
                status = columns[6].text

                founded = False
                idx = None
                if len(self.files) > 0:
                    for index, file in enumerate(self.files):
                        if file["start_date"].strftime('%d/%m/%Y') == date1 and file["end_date"].strftime(
                                '%d/%m/%Y') == date2:
                            founded = True
                            idx = index
                else:
                    self.logger.info("Tous les fichiers ont été téléchargés")
                    break

                founded_file_name = "GlobalBettingHistory" in report_name and \
                                    type == 'CSV' and founded

                if founded_file_name and (status in ["Disponible"]):
                    logger.info("Téléchargement du fichier...")
                    download_button = row.find_element(by=By.XPATH, value=download_button_xpath)
                    WebDriverWait(row, timeout=10).until(EC.element_to_be_clickable(download_button)).click()
                    logger.info("Téléchargement lancé avec succès.")
                    try:
                        name = f"{self.name}_{date1.replace('/', '-')}"
                        file = self._verify_download_opt(start_date=date1, patterns=[date1_formated, date2_formated])
                        file = Path(file)
                        rename_file(file, self.config["download_path"], name, self.logger)
                        sleep(5)
                        del self.files[idx]
                        continue
                    except Exception as e:
                        self.logger.error(
                            f"Le fichier du {date1} n'a pas pu être téléchargé")
                        raise e

                elif founded_file_name and (status in ["En attente", "En cours de traitement"]):
                    self.logger.info(f"Le fichier du {date1} est en attente de téléchargement")
                    sleep(10)
                    self.logger.info("Rétéléchargement du fichier")
                    self._download_files()
                    self.logger.info("Break")
                    break

                # todo: gestion des erreurs
                else:
                    self.logger.error(f"ligne Ignorée")
                    continue

            if len(self.files) > 0:
                sleep(30)
                self._regenerate_files()

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        # self._generate_files()
        #"""
        def generate_date_range(start_date, end_date):
           return [{"start_date": start_date + timedelta(days=i),
                    "end_date": start_date + timedelta(days=i+1)}
                   for i in range((end_date - start_date).days + 1)]

        self.files = generate_date_range(self.start_date, self.end_date)
        #"""
        self._download_files()


def run_sunubet_online():
    env_variables_list = ["SUNUBET_CASINO_LOGIN_USERNAME", "SUNUBET_CASINO_LOGIN_PASSWORD"]
    job = ExtractSunubetOnline(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_sunubet_online()
