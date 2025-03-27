import glob

from base.logger import Logger
from base.web_scrapper import BaseScrapper
# from base.logger import get_logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import datetime

file_path = r"C:\Users\pauli\Downloads\Etat de la course.xls"

def sleep(seconds):
    time.sleep(seconds)

class ExtractGrattageAcajou(BaseScrapper):
    def __init__(self, config, secret_config, logger):
        super().__init__(config, secret_config, logger)

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        browser.get("https://www.pmuonline.sn/lonasemis/lonase_administration/Login.aspx")

        self.logger.info("Saisie des identifiants...")
        usernameId = "Username"
        passwordId = "Password"
        submit_buttonId = "btnSubmit"

        username = 'khady'
        password = 'khady123#'

        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, usernameId))).send_keys(username)

        #Saisie du mot de passe
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, passwordId))).send_keys(password)


        self.logger.info("Envoi du formulaire...")
        #Submit button click
        WebDriverWait(browser,timeout=10*9).until( EC.element_to_be_clickable(( By.ID, submit_buttonId))).click()


        self.logger.info("Vérification de la connexion...")

        try:
            verification_xpath = "/html/body/form/div[3]/table/tbody/tr/td/table[1]/tbody/tr[2]/td[3]/span"

            WebDriverWait(browser,timeout=10*9).until( EC.presence_of_element_located(( By.XPATH, verification_xpath)))
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            print("la connection n'a pas pu etre etablie")
            browser.quit()

        sleep(10)
        pass

    def _go_to_report_page(self):
        browser = self.browser
        self.logger.info("Chargement de la page des rapports...")
        reports_url = "https://www.pmuonline.sn/lonasemis/lonase_administration/HorseDrawWiseSales.aspx"

        delta = datetime.timedelta(days=1)
        end_date = datetime.date.today() #- delta
        delta = datetime.timedelta(days=1)
        start_date = end_date - delta
        liste = []

        year = start_date.strftime("%Y")
        month = start_date.strftime("%m")
        day = start_date.strftime("%d")

        browser.get(reports_url)

        self.logger.info("Remplissage champ date...")

        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlDate"))).select_by_visible_text(str(day))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlDate"))).select_by_visible_text(str(day))

        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlMonth"))).select_by_visible_text(str(month))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlMonth"))).select_by_visible_text(str(month))

        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_FDate_ddlYear"))).select_by_visible_text(str(year))
        (Select(browser.find_element(by=By.ID, value="OpsValidator_ContentPlaceHolder1_TDate_ddlYear"))).select_by_visible_text(str(year))

        self.logger.info("Soumission du formulaire...")
        WebDriverWait(browser,timeout=15).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnSubmit"))).click()

        self.logger.info("Télechargement du fichier...")
        WebDriverWait(browser,timeout=15*3).until( EC.element_to_be_clickable(( By.ID, "OpsValidator_ContentPlaceHolder1_btnExcel"))).click()


        self.logger.info("Vérification du fichier...")
        timer = 30
        while timer>=0:
            # sleep(10)
            timer -= 1

            temp = glob.glob(file_path)
            if len(temp):
                self.logger.info(f"Le fichier du {start_date} a bien été telechargé")
                self.logger.info(f"{temp}")
                sleep(5)
                break

        if timer<0:
            print("Le telechargement est anormalement long, nous allons recommencer")
            # continue

    def _download_files(self):
        pass

    def _exit(self):
            self.browser.quit()

    def process_extraction(self):
        self._open_browser()
        self._connection_to_platform()
        self._go_to_report_page()

def run_gitech():
    config = ""
    secret_config = ""
    logger = Logger(log_file="extract_gitech.log").get_logger()
    job = ExtractGrattageAcajou(config, secret_config, logger)
    job.process_extraction()


if __name__ == "__main__":
    run_gitech()
