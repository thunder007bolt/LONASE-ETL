### system ###
import glob
import pandas as pd
### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.common.by import By
### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import sleep
from datetime import timedelta
from pathlib import Path
import numpy as np
from utils.file_manipulation import delete_file, check_file_not_empty


class ExtractUSSDIRV(BaseScrapper):
    def __init__(self, env_variables_list):
        chrome_options_arguments = [
            "--unsafely-treat-insecure-origin-as-secure=http://dvs2.dyndns.biz:16800/backendcdr/?r=DVS&s=listeappels#form_rech_suivi"
        ]
        super().__init__('ussd_irv', env_variables_list, 'logs/extract_ussd_irv.log',chrome_options_arguments=chrome_options_arguments)
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
        username = secret_config["USSD_IRV_USERNAME"]
        password = secret_config["USSD_IRV_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(usernameId, locator_type='id', timeout=90, keys=username)
        self.wait_and_send_keys(passwordId, locator_type='id', timeout=90, keys=password)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_buttonId, locator_type='id', timeout=90)

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, locator_type='xpath', timeout=90)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        sleep(10)
        pass

    def _delete_old_files(self):
        self.logger.info("Suppression des fichiers existant...")
        delete_file(self.config["download_path"], self.config["file_pattern"])

    def _download_files(self):
       self._process_multiple_files()

    def _process_download(self, start_date, end_date):
        try:
            driver = self.browser
            driver.get("http://dvs2.dyndns.biz:16800/backendcdr/")
            date_str = start_date.strftime("%Y-%m-%d")

            driver.execute_script(f"document.getElementsByName('dateDeb')[0].value = '{date_str}';")
            driver.execute_script(f"document.getElementsByName('dateFin')[0].value = '{date_str}';")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'].chercher"))
            ).click()

            self.logger.info("Telechargement du fichier")
            self.wait_and_click("/html/body/div[3]/form[2]/p[2]", locator_type="xpath", timeout=60*2)

        except Exception as e:
            print(f"Erreur traitement {date_str} : {e}")

    def _process_transformation(self, file_pattern, date):
        self.logger.info("Transformation")
        def convert_xls_to_xlsx(xls_file: Path) -> Path:
            TEMP_DIR = r"C:\Users\optiware2\AppData\Local\Temp\gen_py\3.7"

            def clear_temp():
                try:
                    import shutil
                    shutil.rmtree(TEMP_DIR)
                except OSError as o:
                    print(f"Erreur : {o.strerror}")

            """
            Convertit un fichier XLS en XLSX via l'automatisation COM d'Excel.
            Après conversion, le fichier XLS d'origine est renommé avec un suffixe contenant la date
            et déplacé dans le répertoire des fichiers traités.
            """
            clear_temp()

            self.logger.info(f"Conversion du fichier XLS {xls_file.name} en XLSX...")
            import xlwings as xw
            # Lancement d'Excel (en arrière-plan)
            app = xw.App(visible=False)

            try:
                wb = app.books.open(str(xls_file.resolve()))
                xlsx_file = xls_file.with_suffix(".xlsx")

                if xlsx_file.exists():
                    xlsx_file.unlink()

                wb.save(str(xlsx_file.resolve()))
                wb.close()
            except Exception as e:
                raise e
                app.quit()
            # Renommage et déplacement du fichier XLS d'origine

            return xlsx_file
        self.logger.info("Récupération des informations...")
        self.wait_for_presence("//p[following-sibling::table[@class='tab_suivi']]", raise_error=True)
        paragraphe_info = self.browser.find_element(By.XPATH, "//p[following-sibling::table[@class='tab_suivi']]")
        elements_b = paragraphe_info.find_elements(By.TAG_NAME, "b")
        infos_dict = dict(zip(["Total Appels", "Total Minutes", "Total CA"],
                              [b.text.strip() for b in elements_b[:3]]))
        download_path = Path(self.config["download_path"])
        for file in download_path.glob(f"*{file_pattern}*xls"):
            import pandas as pd
            self.logger.info("Transformation en xlsx")
            xlsx_file = convert_xls_to_xlsx(file)
            file.unlink()
            df = pd.read_excel(xlsx_file, sheet_name=0, dtype=str)

            df['DATE APPEL'] = df['DATE APPEL'].str.replace('-', '/')
            df['DATE APPEL'] = df['DATE APPEL'].str[:16]
            df['JOUR'] = df['DATE APPEL'].str[:10]
            df = df[
                df['DATE APPEL'].notna() & (df['DATE APPEL'] != 'nan') &
                df['NUMERO APPELANT'].notna() & (df['NUMERO APPELANT'] != 'nan') &
                df['NUMERO SERVEUR'].notna() & (df['NUMERO SERVEUR'] != 'nan')
                ]

            # Fonction de conversion en HH:MM:SS
            def secondes_to_hhmmss(total_seconds):
                total_seconds = int(total_seconds)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                if hours > 0:
                    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                else:
                    return f"{int(minutes):02}:{int(seconds):02}"

            # Appliquer la conversion
            df['DUREE APPEL'] = df['DUREE APPEL'].apply(secondes_to_hhmmss)
            df["Total Appels"] = ""
            df["Total CA"] = ""

            print(df.size, len(df), "taille")
            if df.size == 0:
                self.logger.info(f'Le fichier du {date.strftime("%Y-%m-%d")} est vide')
                continue

            df.iloc[0, df.columns.get_loc("Total Appels")] = infos_dict.get("Total Appels")
            df.iloc[0, df.columns.get_loc("Total CA")] = infos_dict.get("Total CA")
            #Nettoyage de la colonne Total Appels
            df["Total Appels"] = df["Total Appels"].astype(str).str.replace(" ", "").str.replace(",", "")
            # Nettoyage de la colonne Total CA
            df["Total CA"] = df["Total CA"].astype(str).str.replace("FCFA", "").str.replace(" ", "").str.replace(",", "")

            col_order = ["DATE APPEL","JOUR", "NUMERO SERVEUR", "NUMERO APPELANT", "DUREE APPEL", "Total Appels", "Total CA"]
            col_remame = {
                "DATE APPEL":"Date Appel",
                "JOUR":"Jour",
                "NUMERO SERVEUR": "Numéro Serveur",
                "NUMERO APPELANT": "Numéro Appelant",
                "DUREE APPEL": "Durée Appel",
            }
            df = df[col_order]
            df = df.rename(columns=col_remame)
            # Repertoire cible
            df = df.replace(np.nan, '')
            self.logger.info("Sauvegarde final...")
            df.to_csv(f"{self.transformation_dest_path / file_pattern}.csv", index=False, sep=';',encoding='utf-8-sig')
            import os
            date_str = date.strftime("%Y-%m-%d")
            chemin_fichier = os.path.join(r"K:\DATA_FICHIERS\USSD", f"GFM_CDR_DETAILS_{date_str}.csv")
            df.to_csv(chemin_fichier, index=False, sep=';', encoding='utf-8-sig')
            xlsx_file.unlink()
            self.logger.info(f"Transformation du fichier {file} réussie")

def run_ussd_irv():
    env_variables_list = ["USSD_IRV_USERNAME", "USSD_IRV_PASSWORD"]
    job = ExtractUSSDIRV(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_ussd_irv()
