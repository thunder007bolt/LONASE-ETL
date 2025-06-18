### system ###
### base ###
from pathlib import Path

import pandas as pd
### selenium ###
from base.web_scrapper import BaseScrapper
### utils ###
from utils.date_utils import sleep


class ExtractPmuCA(BaseScrapper):
    def __init__(self, env_variables_list,  config_path=None, log_file=None):
        super().__init__('pmu_ca', env_variables_list, log_file or 'logs/extract_pmu_ca.log', config_path=config_path)
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        login_step1_xpath = html_elements["login_step1_xpath"]
        login_step2_xpath = html_elements["login_step2_xpath"]
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["PMU_LOGIN_USERNAME"]
        password = secret_config["PMU_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_click(login_step1_xpath, locator_type='xpath', timeout=60*10, raise_error=True)
        self.wait_and_click(login_step2_xpath, locator_type='xpath')
        self.wait_and_send_keys(username_xpath, locator_type='xpath', keys=username, raise_error=True)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath')

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_element_visible(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")
        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()
        sleep(10)
        pass

    def _download_files(self):
       self._process_multiple_files()

    def _process_download(self, start_date, end_date):
        browser = self.browser
        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        date_element_xpath = html_elements["date_element_xpath"]
        date_month_element_xpath = html_elements["date_month_element_xpath"]
        step1_element_xpath = html_elements["step1_element_xpath"]
        step2_element_xpath = html_elements["step2_element_xpath"]
        step3_element_xpath = html_elements["step3_element_xpath"]

        # print(date.strftime('%m'))   # "02"
        # print(date.strftime('%#m'))  # "2"
        month = start_date.strftime('%#m')
        date_month_element_xpath = date_month_element_xpath.replace('variable_to_be_set', month)
        date = start_date.strftime('%d-%m-%Y')
        date_element_xpath = date_element_xpath.replace('variable_to_be_set', date)

        self.wait_and_click(date_month_element_xpath, locator_type="xpath", timeout=120)
        sleep(5)
        self.wait_and_click(date_element_xpath, locator_type="xpath", timeout=120)
        self.wait_and_click(date_element_xpath, locator_type="xpath", timeout=120)
        sleep(10)

        step1_element_xpath = step1_element_xpath.replace('variable_to_be_set', date)
        self.wait_for_presence(step1_element_xpath, raise_error=True)

        #todo: verifier si les valeurs ont changé
        sleep(5)
        table1 = self.wait_for_click(step2_element_xpath, raise_error=True)
        df = pd.read_html(table1.get_attribute('outerHTML'))
        df = df[0].dropna(axis=0, thresh=4)

        table2 = self.wait_for_click(step3_element_xpath, raise_error=True)
        df2 = pd.read_html(table2.get_attribute('outerHTML'))
        df2 = df2[0].dropna(axis=0, thresh=4)

        df_concatenated = pd.concat([df.transpose(), df2.transpose()], axis=1)
        df_concatenated = df_concatenated.set_axis(['CA', 'SHARING'], axis=1)  # , 'Z'
        df_concatenated.index.name = 'PRODUIT'

        for index, row in df_concatenated.iterrows():
            for column in df_concatenated.columns:
                df_concatenated.at[index, column] = str(row[column]).strip().replace('\u202f', ' ').lstrip("CA :")

        df_concatenated = pd.DataFrame(data=df_concatenated);

        df_concatenated['JOUR'] = str(start_date.strftime('%d/%m/%Y'))
        df_concatenated['ANNEE'] = str(start_date.strftime('%Y'))
        df_concatenated['MOIS'] = str(start_date.strftime('%m'))

        try:
            self.logger.info(f"Enregistrement du fichier PMU Senegal du {start_date} ...")
            filename = "Pmu_Senegal_ca_" + str(self.start_date) + ".csv"
            df = df_concatenated[:-2]
            # todo: update path
            destination = Path(self.config["download_path"])
            final_file = destination / filename
            df.to_csv(final_file, sep=';', encoding='utf8')

        except Exception as e:
            self.logger.error(f"Erreur lors de la telechargement du fichier PMU Senegal : {e}")
            raise e

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()


def run_pmu_ca(config_path=None, log_file=None):
    env_variables_list = ["PMU_LOGIN_USERNAME", "PMU_LOGIN_PASSWORD"]
    job = ExtractPmuCA(env_variables_list, config_path=config_path, log_file=log_file)
    job.process_extraction()


if __name__ == "__main__":
    run_pmu_ca()
