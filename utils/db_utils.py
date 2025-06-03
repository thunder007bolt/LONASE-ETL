import pyodbc
import oracledb
import os
# from hdbcli import dbapi

def get_db_connection(db_server, db_name, db_user, db_password, db_type="sql_server", logger=None):

    if db_type == "sql_server":
        driver = "ODBC Driver 17 for SQL Server"
    elif db_type == "mysql":
        driver = "MySQL ODBC 9.1 ANSI Driver"
    else:
        raise NameError(f'Unsupported connexion db_type: {db_type}')

    try:
        if logger:
            logger.info("Connection à la base de données...")
        connection = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={db_server};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password}"
        )

        cursor = connection.cursor()
        if logger: logger.info("Connexion à la base de données réussie")

        return connection, cursor

    except Exception as e:
        print(f" error: {e}")
        if logger: logger.error(
            f"Erreur lors de la connexion à la base de données: {e}")
        return None, None

def get_oracle_connection(username, password, host, port, service_name, lib_dir=None, logger=None):
    try:
        # Active le mode "thick" si un répertoire client est fourni
        if lib_dir:
            if not os.environ.get("PATH", "").startswith(lib_dir):
                oracledb.init_oracle_client(lib_dir=fr"{lib_dir}")
                if logger:
                    logger.info(f"Oracle client initialized with lib_dir: {lib_dir}")
    except Exception as e:
        if logger:
            logger.warning(f"Oracle client initialization issue (might be already initialized): {e}")

    try:
        dsn = f"{host}:{port}/{service_name}"
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        if logger:
            logger.info(f"Successfully connected to Oracle DB: {username}@{host}:{port}/{service_name}")
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to Oracle DB {username}@{host}:{port}/{service_name}: {e}")
        raise
    

# def get_sap_db_connection(db_server, db_port, db_user, db_password, logger=None):
#     try:
#         if logger: logger.info("Connection to the sap database...")
#         connection = dbapi.connect(
#             address=db_server,
#             port=db_port,
#             user=db_user,
#             password=db_password
#         )
#         cursor = connection.cursor()
#         return connection, cursor

#     except Exception as e:
#         print(f" error: {e}")
#         if logger: logger.error(f"Error connecting to the sap database: {e}")
#         return None