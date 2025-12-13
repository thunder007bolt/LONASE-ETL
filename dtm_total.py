import time
from utils.config_utils import get_secret
from utils.constants import TEMP_DB_ENV_VARIABLES_LIST
from utils.db_utils import get_db_connection

# Récupération des secrets
secret_config = get_secret([
    "SQL_SERVER_HOST",
    "SQL_SERVER_DB_NAME",
    "SQL_SERVER_DB_USERNAME",
    "SQL_SERVER_DB_PASSWORD"
])

# Connexion à SQL Server
SERVER = secret_config['SQL_SERVER_HOST']
DATABASE = secret_config['SQL_SERVER_DB_NAME']
USERNAME = secret_config['SQL_SERVER_DB_USERNAME']
PASSWORD = secret_config['SQL_SERVER_DB_PASSWORD']
connexion, cursor = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD)

# Nom du job SQL Server à exécuter
job_name = 'ANNUEL_PACK_DTM_TOTAL'

# Lancer le job
try:
    cursor.execute("EXEC msdb.dbo.sp_start_job @job_name = ?", job_name)
    connexion.commit()
    print(f"Le job '{job_name}' a été lancé avec succès.")
except Exception as e:
    print("Erreur lors du lancement du job :", e)
    raise

time.sleep(10)
# Obtenir l'ID du job
cursor.execute("""
    SELECT job_id 
    FROM msdb.dbo.sysjobs 
    WHERE name = ?
""", job_name)
row = cursor.fetchone()
if not row:
    raise Exception(f"Job '{job_name}' introuvable.")
job_id = row[0]

# Attendre la fin du job
print("Attente de la fin du job...")
while True:
    cursor.execute("""
        SELECT ja.start_execution_date, ja.stop_execution_date, ja.run_requested_date, ja.run_requested_source, 
               ISNULL(ja.stop_execution_date, '1900-01-01') as stop_date, 
               sjs.last_run_outcome
        FROM msdb.dbo.sysjobactivity ja
        JOIN msdb.dbo.sysjobs sj ON ja.job_id = sj.job_id
        LEFT JOIN msdb.dbo.sysjobservers sjs ON sj.job_id = sjs.job_id
        WHERE sj.job_id = ? AND ja.stop_execution_date IS NULL AND  cast(ja.start_execution_date as date) = cast( sysdatetime() as date)
    """, job_id)
    row = cursor.fetchone()

    if row is None:
        print("Le job est terminé.")
        break
    else:
        print("Le job est toujours en cours...")
        time.sleep(30)  # Attendre 5 secondes avant de vérifier à nouveau

print("Fin de traitement.")
