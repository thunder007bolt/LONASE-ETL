
from utils.config_utils import get_secret
from utils.constants import TEMP_DB_ENV_VARIABLES_LIST
from utils.db_utils import get_db_connection

secret_config= get_secret(
   [
       "SQL_SERVER_HOST",
       "SQL_SERVER_DB_NAME",
       "SQL_SERVER_DB_USERNAME",
       "SQL_SERVER_DB_PASSWORD"
   ]
)
# Connexion à SQL Server
SERVER = secret_config['SQL_SERVER_HOST']
DATABASE = secret_config['SQL_SERVER_DB_NAME']
USERNAME = secret_config['SQL_SERVER_DB_USERNAME']
PASSWORD = secret_config['SQL_SERVER_DB_PASSWORD']
connexion, cursor = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD)

# Nom du job SQL Server à lancer
job_name = 'PRD_PACK_FINAL_DC'

try:
    cursor.execute("EXEC msdb.dbo.sp_start_job @job_name = ?", job_name)
    connexion.commit()
    print(f"Le job '{job_name}' a été lancé avec succès.")
except Exception as e:
    print("Erreur lors du lancement du job :", e)
    raise e
