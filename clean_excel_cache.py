TEMP_DIR = r"C:\Users\OPTIWA~1\AppData\Local\Temp\gen_py\3.13"
import shutil
shutil.rmtree(TEMP_DIR)

import win32com.client.gencache
win32com.client.gencache.is_readonly = False
win32com.client.gencache.Rebuild()
TEMP_DIR = r"C:\Users\OPTIWA~1\AppData\Local\Temp\gen_py\3.13"
SCRIPTS_DIR = r"C:\ETL\Base"
JOURNALIER_DIR = r"C:\ETL\Base\journalier"

processes = []
try:
    import os
    os.system("taskkill /im excel.exe /f")
except Exception as e:
    print(f"Erreur lors de la fermeture d'Excel : {e}")

try:
    shutil.rmtree(TEMP_DIR)
except OSError as o:
    print(f"Erreur : {o.strerror}")
