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
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date, sleep
from utils.other_utils import move_file, loading, retry_operation
from utils.file_manipulation import rename_file


class ExtractEditecLoto(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('editec_loto', env_variables_list,
                         'logs/extract_editec_loto.log')
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
        self.wait_and_send_keys(username_xpath, locator_type='xpath', timeout=90, keys=username)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', timeout=90, keys=password)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath', timeout=90)
        sleep(2)

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, locator_type='xpath', timeout=10)
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
            calendar_start_xpath = html_elements["calendar_start_xpath"]
            calendar_start_button_xpath = html_elements["calendar_start_button_xpath"]
            calendar_start_month_year_xpath = html_elements["calendar_start_month_year_xpath"]
            calendar_start_day_xpath = html_elements["calendar_start_day_xpath"]
            real_start_date = start_date - delta
            real_end_date = start_date + delta
            self.wait_and_click(
                "/html/body/hg-root/hg-layout/div/div/div/hg-create-report/div/ngb-accordion/div[1]/div[2]/div/hg-create-report-button/button",
                locator_type="xpath")


            sleep(1)

            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)

            self.wait_and_click(calendar_start_xpath, locator_type="xpath")
            self.wait_and_click(calendar_start_button_xpath, locator_type="xpath")

            for i in browser.find_elements(by=By.XPATH, value=calendar_start_month_year_xpath):
                if real_start_date.strftime('%Y') in i.text:
                    i.click()
                    break
            sleep(1)
            for i in browser.find_elements(by=By.XPATH, value=calendar_start_month_year_xpath):
                t = real_start_date.strftime('%b')
                if t == 'Dec':
                    t = 'Déc'
                if t in i.text:
                    i.click()
                    break
            sleep(1)
            for i in browser.find_elements(by=By.XPATH, value=calendar_start_day_xpath):
                if (str(0) + i.text.strip())[-2:] in real_start_date.strftime('%d'):
                    i.click()
                    break
            sleep(1)

            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)

            logger.info("Date fin")
            calendar_end_xpath = html_elements["calendar_end_xpath"]
            calendar_end_button_xpath = html_elements["calendar_end_button_xpath"]
            calendar_end_month_year_xpath = html_elements["calendar_end_month_year_xpath"]
            calendar_end_day_xpath = html_elements["calendar_end_day_xpath"]
            self.wait_and_click(calendar_end_xpath, locator_type="xpath")
            self.wait_and_click(calendar_end_button_xpath, locator_type="xpath")
            # self.wait_and_click(
            #     "html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[2]/hg-calendar/div/p-calendar/span/div/div[2]/div[3]/button[1]",
            #     locator_type="xpath")
            # self.wait_and_click(
            #     "html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[2]/hg-calendar/div/p-calendar/span/div/div[2]/div[1]/button[1]",
            #     locator_type="xpath")
            # self.wait_and_click(
            #     "html/body/ngb-popover-window/div[2]/hg-report-request-generator/form/div[2]/hg-calendar/div/p-calendar/span/div/div[1]/div/div[1]/div/button[2]",
            #     locator_type="xpath")
            sleep(2)
            for i in browser.find_elements(by=By.XPATH, value=calendar_end_month_year_xpath):
                if real_end_date.strftime('%Y') in i.text:
                    i.click()
                    break
            sleep(2)
            for i in browser.find_elements(by=By.XPATH, value=calendar_end_month_year_xpath):
                t = real_start_date.strftime('%b')
                if t == 'Dec':
                    t = 'Déc'
                if t in i.text:
                    i.click()
                    break
            sleep(2)
            for i in browser.find_elements(by=By.XPATH, value=calendar_end_day_xpath):
                if (str(0) + i.text.strip())[-2:] in real_end_date.strftime('%d'):
                    i.click()
                    break
            sleep(1)

            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)
            dropdown_ng_select_xpath = self.config['html_elements']['category_dropdown_ng_select_xpath']

            self._manage_dropdown_state('open', dropdown_ng_select_xpath)

            category_option_xpath = html_elements["category_options_xpath"]
            current_elements_in_dropdown = browser.find_elements(By.XPATH, category_option_xpath)
            for el_sel in current_elements_in_dropdown:
                if el_sel.text.strip() == 'Loterie':
                    el_sel.click()
                    break

            self._manage_dropdown_state('close', dropdown_ng_select_xpath)
            dropdown_ng_select_xpath = self.config['html_elements']['etat_ticket_dropdown_ng_select_xpath']
            etat_ticket_all_button = self.config['html_elements']['etat_ticket_all_button']
            self._manage_dropdown_state('open', dropdown_ng_select_xpath)
            self.wait_and_click(etat_ticket_all_button, locator_type="xpath")
            self._manage_dropdown_state('close', dropdown_ng_select_xpath)
            logger.info("Soumission du formulaire...")
            submit_button_xpath = html_elements["report_submit_button_xpath"]
            self.wait_and_click(submit_button_xpath, locator_type="xpath")
            sleep(5)
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
                start_date_formated = (start_date - delta).strftime('%d/%m/%Y')
                end_date_formated = (start_date + delta).strftime('%d/%m/%Y')
                columns = row.find_elements(by=By.TAG_NAME, value="td")
                if len(columns) < 5:
                    continue
                logger.info(f"Report name: {columns[1].text}, Dates: {columns[2].text}, {columns[3].text}, Status: {columns[4].text}")
                report_name = columns[2].text
                type = columns[3].text
                date1 = columns[4].text
                date2 = columns[5].text
                status = columns[6].text
                founded_file_name = "TicketHistory" in report_name and \
                                    type == 'CSV' and \
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
        #""""
        def generate_date_range(start_date, end_date):
              return [{"start_date": start_date + timedelta(days=i),
                       "end_date": start_date + timedelta(days=i)}
                      for i in range((end_date - start_date).days + 1)]

        self.files = generate_date_range(self.start_date, self.end_date)
        #"""
        self._download_files()

def run_editec_loto():
    env_variables_list = ["EDITEC_LOTO_LOGIN_USERNAME", "EDITEC_LOTO_LOGIN_PASSWORD"]
    job = ExtractEditecLoto(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_editec_loto()
