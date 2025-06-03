import pandas as pd
import numpy as np
import datetime
import time
import pyodbc
import cx_Oracle # Make sure this is installed: pip install oracledb or cx_Oracle
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import timedelta

# Assume these utility functions exist as shown in the provided context
# from utils.config_utils import get_secret, get_config, get_database_extractor_configurations
# from utils.db_utils import get_db_connection
# from utils.file_manipulation import move_file
# from utils.date_utils import get_yesterday_date

# --- Mock Utility Functions (Replace with your actual implementations) ---
# These are simplified mocks for demonstration if you don't have the utils
import logging
import os

def get_oracle_connection(username, password, host, port, service_name, lib_dir, logger=None):
    try:
        if lib_dir and not os.environ.get("PATH", "").startswith(lib_dir):
             cx_Oracle.init_oracle_client(lib_dir=lib_dir)
             if logger:
                 logger.info(f"Oracle client initialized with lib_dir: {lib_dir}")
    except Exception as e:
        # Might fail if already initialized, often safe to ignore
         if logger:
              logger.warning(f"Oracle client initialization issue (might be already initialized): {e}")

    try:
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        conn = cx_Oracle.connect(username, password, dsn, encoding='UTF-8')
        if logger:
            logger.info(f"Successfully connected to Oracle DB: {username}@{host}:{port}/{service_name}")
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to Oracle DB {username}@{host}:{port}/{service_name}: {e}")
        raise # Re-raise the exception

# --- Base DatabaseExtractor Class (Minimal version from context) ---
delta_day = timedelta(days=1)

class DatabaseExtractor(ABC):
    def __init__(self, name, log_file, env_variables_list):
        self.name = name
        self.log_file = log_file
        (
            self.secret_config,
            self.config,
            self.logger,
            self.extraction_dest_path # Path for potential outputs
        ) = get_database_extractor_configurations(name, log_file, env_variables_list)
        # Initialize connections to None
        self.conn_sql_source = None
        self.cursor_sql_source = None
        self.conn_sql_proc = None
        self.cursor_sql_proc = None
        self.conn_oracle_target = None
        self.cursor_oracle_target = None
        self.start_date = None # Will be set by _set_date
        self.annee = None
        self.mois = None
        self.jour = None


    def _connect_sql_source(self):
        try:
            self.conn_sql_source, self.cursor_sql_source = get_db_connection(
                server=self.secret_config['SQLSERVER_SOURCE_SERVER'],
                database=self.secret_config['SQLSERVER_SOURCE_DATABASE'],
                username=self.secret_config['SQLSERVER_SOURCE_USERNAME'],
                password=self.secret_config['SQLSERVER_SOURCE_PASSWORD'],
                logger=self.logger
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Source SQL Server: {e}")
            return False

    def _connect_sql_proc(self):
         try:
            self.conn_sql_proc, self.cursor_sql_proc = get_db_connection(
                server=self.secret_config['SQLSERVER_PROC_SERVER'],
                database=self.secret_config['SQLSERVER_PROC_DATABASE'],
                username=self.secret_config['SQLSERVER_PROC_USERNAME'],
                password=self.secret_config['SQLSERVER_PROC_PASSWORD'],
                logger=self.logger
            )
            return True
         except Exception as e:
            self.logger.error(f"Failed to connect to Processing SQL Server: {e}")
            return False

    def _connect_oracle_target(self):
        try:
            self.conn_oracle_target, self.cursor_oracle_target = get_oracle_connection(
                username=self.secret_config['ORACLE_TARGET_USERNAME'],
                password=self.secret_config['ORACLE_TARGET_PASSWORD'],
                host=self.secret_config['ORACLE_TARGET_HOST'],
                port=self.secret_config['ORACLE_TARGET_PORT'],
                service_name=self.secret_config['ORACLE_TARGET_SERVICE'],
                lib_dir=self.secret_config.get('ORACLE_CLIENT_LIB_DIR'), # Use .get for optional param
                logger=self.logger
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Target Oracle DB: {e}")
            return False

    def _close_connections(self):
        connections = [
            (self.cursor_sql_source, self.conn_sql_source, "Source SQL"),
            (self.cursor_sql_proc, self.conn_sql_proc, "Processing SQL"),
            (self.cursor_oracle_target, self.conn_oracle_target, "Target Oracle")
        ]
        for cursor, conn, name in connections:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                self.logger.info(f"{name} connection closed.")
            except Exception as e:
                self.logger.warning(f"Could not close {name} connection: {e}")

    @abstractmethod
    def _load_data_from_db(self):
        """Extracts data from the source database."""
        pass

    @abstractmethod
    def _process_data(self, data):
        """Transforms the extracted data."""
        pass

    @abstractmethod
    def _load_data_to_target(self, data):
        """Loads data into the target database."""
        pass

    def _set_date(self):
        """Calculates the specific date (jour, mois, annee) for the commission."""
        # Use today's date for calculation base unless start_date is forced in config
        base_date = self.config.get("start_date") or datetime.date.today()
        # Ensure base_date is a date object if parsed from config string
        if isinstance(base_date, str):
             try:
                 base_date = datetime.datetime.strptime(base_date, "%Y-%m-%d").date()
             except ValueError:
                 self.logger.error(f"Invalid date format in config: {base_date}. Using today.")
                 base_date = datetime.date.today()

        self.logger.info(f"Calculating commission date based on: {base_date}")

        jour_date = None
        if base_date.day < 15:
            # First day of the current month, then subtract one day to get previous month's end
            first_day_current_month = datetime.date(base_date.year, base_date.month, 1)
            jour_date = first_day_current_month - delta_day # Will be 15th or end of prev month
            # Logic correction: Need 15th of previous month or last day of month before previous.
            # Let's follow the original script's logic: < 15 means use 15th of *previous* month
            prev_month_date = first_day_current_month - delta_day
            jour_date = datetime.date(prev_month_date.year, prev_month_date.month, 15)

        else: # Day is >= 15
            # Use the 1st of the current month
             jour_date = datetime.date(base_date.year, base_date.month, 1)
            # Original logic seems to aim for 15th of current month if run date >=15
            # Let's refine: if today >= 15, target date is 1st of current month.
            # If today < 15, target date is 15th of *previous* month.

        # --- Re-evaluating original logic ---
        # if int(end_date.strftime("%d")) < 15 :
        #     # jour = 1st day of current month - 1 day delta => Last day of previous month
        #     # Then it was overwritten? jour = datetime.date(..., 15) ??
        #     jour = datetime.date((end_date).year, (end_date).month, 1) - delta
        # else:
        #     # jour = 15th day of current month
        #     jour = datetime.date((end_date - delta).year, (end_date - delta).month, 15)
        # jour = datetime.date(2025, 4, 15) # This hardcoding overrides everything!

        # Let's implement a clearer logic based on common patterns:
        # Run between 1st-14th: Process for 15th of *previous* month.
        # Run between 15th-31st: Process for 1st of *current* month.
        today = datetime.date.today()
        target_date = None
        if today.day < 15:
            first_day_current_month = datetime.date(today.year, today.month, 1)
            prev_month_last_day = first_day_current_month - delta_day
            target_date = datetime.date(prev_month_last_day.year, prev_month_last_day.month, 15)
            self.logger.info(f"Today is {today.day} (<15), setting target date to 15th of previous month: {target_date}")
        else:
             target_date = datetime.date(today.year, today.month, 1)
             self.logger.info(f"Today is {today.day} (>=15), setting target date to 1st of current month: {target_date}")

        # Override with config if provided
        if self.config.get("force_target_date"):
             try:
                 target_date = datetime.datetime.strptime(self.config["force_target_date"], "%Y-%m-%d").date()
                 self.logger.warning(f"Overriding calculated target date with forced date: {target_date}")
             except ValueError:
                 self.logger.error(f"Invalid force_target_date format: {self.config['force_target_date']}. Using calculated date.")


        self.start_date = target_date # Store the calculated date
        self.annee = target_date.year
        self.mois = target_date.strftime("%m")
        self.jour = target_date.strftime("%d")
        self.logger.info(f"Commission date set to: Annee={self.annee}, Mois={self.mois}, Jour={self.jour}")


    def _call_stored_procedure(self):
        """Calls the commission processing stored procedure."""
        if not self.conn_sql_proc or not self.cursor_sql_proc:
             self.logger.error("Processing SQL Server connection not available.")
             return False
        try:
            self.logger.info(f"Calling PROC_COMMISSION with Annee={self.annee}, Mois={self.mois}, Jour={self.jour}")
            # Ensure parameters are passed correctly (check procedure definition if issues arise)
            self.cursor_sql_proc.execute("{CALL [USER_DWHPR].[PROC_COMMISSION](?, ?, ?)}",
                                         (str(self.annee), str(self.mois).zfill(2), str(self.jour).zfill(2)))
            self.conn_sql_proc.commit()
            self.logger.info("Successfully called PROC_COMMISSION.")
            return True
        except Exception as e:
            self.logger.error(f"Error calling PROC_COMMISSION: {e}")
            # Consider rolling back if necessary, though it's a SELECT call in the original context?
            # self.conn_sql_proc.rollback()
            return False

    # We replace process_extraction to handle the specific multi-DB workflow
    def process_extraction(self):
        """Orchestrates the commission extraction, processing, and loading."""
        self.logger.info(f"Starting commission processing job: {self.name}")
        data = None
        success = False
        try:
            self._set_date() # Calculate target annee, mois, jour

            # Establish all connections
            if not self._connect_sql_source(): return
            if not self._connect_sql_proc(): return
            if not self._connect_oracle_target(): return

            # Step 1: Call Stored Procedure (as done twice in the original script)
            # It seems the SP might prepare data before extraction?
            if not self._call_stored_procedure():
                 self.logger.error("Failed during initial stored procedure call. Aborting.")
                 return # Abort if SP call fails

            # Step 2: Extract data from source SQL Server
            data = self._load_data_from_db()
            if data is None or data.empty:
                self.logger.warning("No commission data found after initial SP call. Exiting.")
                return # Exit if no data

            # Step 3: Call Stored Procedure again (if needed, as per original script)
            # self.logger.info("Calling stored procedure again after data check...")
            # if not self._call_stored_procedure():
            #      self.logger.error("Failed during second stored procedure call. Aborting.")
            #      return # Abort if SP call fails

            # Step 4: Process/Transform data
            transformed_data = self._process_data(data)
            if transformed_data is None:
                self.logger.error("Data transformation failed. Aborting.")
                return

            # Step 5: Load data into target Oracle DB
            load_success = self._load_data_to_target(transformed_data)
            if not load_success:
                 self.logger.error("Loading data to Oracle failed.")
                 # Decide on rollback strategy if needed (e.g., if partial loads occurred)
            else:
                 self.logger.info("Commission data successfully processed and loaded.")
                 success = True

        except Exception as e:
            self.logger.exception(f"An unexpected error occurred during commission processing: {e}")
            # Rollback Oracle transaction if applicable and connection exists
            if self.conn_oracle_target:
                 try:
                      self.conn_oracle_target.rollback()
                      self.logger.info("Oracle transaction rolled back due to error.")
                 except Exception as rb_err:
                      self.logger.error(f"Failed to rollback Oracle transaction: {rb_err}")

        finally:
            # Always close connections
            self._close_connections()
            self.logger.info(f"Commission processing job finished. Success: {success}")

# --- Concrete Implementation for Commission Extraction ---

class ExtractCommission(DatabaseExtractor):
    def __init__(self, env_variables_list):
        super().__init__('commission_extraction', 'extract_commission.log', env_variables_list)

    def _load_data_from_db(self):
        """Extracts commission data from the LONASE_SIC database."""
        if not self.conn_sql_source or not self.cursor_sql_source:
            self.logger.error("Source SQL Server connection not available.")
            return None

        query = f"""
            SELECT *
            FROM [dbo].[commission_bi] -- Use schema name if necessary
            WHERE year([QUINZAINE])= ?
              AND MONTH([QUINZAINE])= ?
              AND DAY([QUINZAINE]) = ?
        """
        try:
            self.logger.info(f"Extracting data for {self.annee}-{self.mois}-{self.jour} from source.")
            # Use parameters to prevent SQL injection
            data = pd.read_sql_query(query, self.conn_sql_source, params=[self.annee, self.mois, self.jour])
            if data.empty:
                self.logger.warning("No data returned from commission_bi table for the specified date.")
            else:
                self.logger.info(f"Successfully extracted {len(data)} rows from source.")
            return data
        except Exception as e:
            self.logger.error(f"Error executing query on source SQL Server: {e}")
            return None

    def _process_data(self, data):
        """Transforms the extracted commission data."""
        if data is None:
            return None
        try:
            self.logger.info("Starting data transformation...")
            # Handle potential date format variations ('%Y-%m-%d' or '%d-%m-%Y')
            def parse_date_flexible(date_str):
                for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        # Handle potential time part like ' 00:00:00'
                        date_part = str(date_str).split(' ')[0]
                        return datetime.datetime.strptime(date_part, fmt).strftime("%d/%m/%Y")
                    except ValueError:
                        pass
                self.logger.warning(f"Could not parse date: {date_str} with known formats. Returning original.")
                return str(date_str) # Return original if parsing fails

            # Apply date formatting (make sure column name 'QUINZAINE' is correct)
            if 'QUINZAINE' in data.columns:
                 self.logger.info("Formatting QUINZAINE column...")
                 # data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%Y-%m-%d").strftime("%d/%m/%Y") for i in data['QUINZAINE']]
                 # data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%d-%m-%Y").strftime("%d/%m/%Y") for i in data['QUINZAINE']] # Original had two attempts
                 data['QUINZAINE'] = data['QUINZAINE'].apply(parse_date_flexible)
                 self.logger.info("QUINZAINE formatting complete.")
            else:
                 self.logger.warning("Column 'QUINZAINE' not found for date formatting.")


            # Replace NaN with empty string
            self.logger.info("Replacing NaN values...")
            data = data.replace(np.nan, '')
            self.logger.info("NaN replacement complete.")

            # Convert all fields to string and replace decimal point '.' with ','
            self.logger.info("Converting fields to string and replacing decimal points...")
            # Applymap might be slow on large dataframes, consider column-wise if needed
            data = data.astype(str).applymap(lambda x: x.replace('.', ','))
            self.logger.info("String conversion and decimal point replacement complete.")

            self.logger.info("Data transformation finished successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Error during data transformation: {e}")
            return None


    def _load_data_to_target(self, data):
        """Loads the transformed data into the Oracle target database."""
        if not self.conn_oracle_target or not self.cursor_oracle_target:
            self.logger.error("Target Oracle connection not available.")
            return False
        if data is None or data.empty:
             self.logger.warning("No data provided to load into Oracle target.")
             return True # Nothing to load is not an error here

        try:
            self.logger.info("Preparing data for Oracle insertion...")
            # Convert DataFrame records to list of tuples
            data_tuples = list(data.to_records(index=False))
            self.logger.info(f"Converted {len(data_tuples)} rows to tuples.")

            # 1. Truncate temporary table
            self.logger.info("Truncating OPTIWARETEMP.SRC_COMMISSION_PRD...")
            self.cursor_oracle_target.execute("TRUNCATE TABLE OPTIWARETEMP.SRC_COMMISSION_PRD")
            self.logger.info("Truncate complete.")

            # 2. Insert data into temporary table
            self.logger.info(f"Inserting {len(data_tuples)} rows into OPTIWARETEMP.SRC_COMMISSION_PRD...")
            insert_sql = """
                INSERT INTO OPTIWARETEMP.SRC_COMMISSION_PRD (
                    "QUINZAINE", "AGENCE", "PRODUIT", "IDENTIFIANT", "PRENOM", "NOM",
                    "CA_CAL", "CA_V", "REMB", "COM_B", "ECART", "RET_F", "DEC_AN",
                    "ENG", "MUS", "DEC_AC", "REGUL", "COM_N"
                ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18)
            """
            # Adjust column count (:1 to :18) based on actual columns in data_tuples
            if len(data.columns) != 18:
                 self.logger.error(f"Data has {len(data.columns)} columns, but insert statement expects 18. Check query and table structure.")
                 return False

            self.cursor_oracle_target.executemany(insert_sql, data_tuples, batcherrors=True)

            # Check for batch errors
            errors = self.cursor_oracle_target.getbatcherrors()
            if errors:
                for error in errors:
                    self.logger.error(f"Error inserting row {error.offset}: {error.message}")
                self.conn_oracle_target.rollback() # Rollback on insertion errors
                self.logger.error("Rolling back due to insertion errors.")
                return False
            else:
                self.logger.info("Bulk insert into temporary table complete.")


            # 3. Delete from final table based on temporary table dates
            self.logger.info("Deleting existing records from USER_DWHPR.SIC_COMMISSION for the target period...")
            # Note: This assumes QUINZAINE in SRC_COMMISSION_PRD is 'dd/mm/yyyy' and DIM_TEMPS.JOUR matches this format.
            # Ensure date formats are compatible for the join/subquery.
            delete_sql = """
                DELETE FROM USER_DWHPR.SIC_COMMISSION
                WHERE IDTEMPS IN (
                    SELECT DISTINCT T.IDTEMPS
                    FROM USER_DWHPR.DIM_TEMPS T
                    JOIN OPTIWARETEMP.SRC_COMMISSION_PRD S ON T.JOUR = S.QUINZAINE
                )
            """
            self.cursor_oracle_target.execute(delete_sql)
            self.logger.info(f"{self.cursor_oracle_target.rowcount} rows deleted from SIC_COMMISSION.")


            # 4. Insert into final table from temporary table with transformations
            self.logger.info("Inserting processed data into USER_DWHPR.SIC_COMMISSION...")
            insert_select_sql = """
                INSERT INTO "USER_DWHPR"."SIC_COMMISSION" (
                    IDENTIFIANT, IDTEMPS, AGENCE, SHOPS, PRODUIT, CA_CAL, CA_V, REMB,
                    COM_B, ECART, RET_F, DEC_AN, ENG, MUS, DEC_AC, REGUL, COM_N
                )
                SELECT
                    F.IDENTIFIANT, Te.IDTEMPS,
                    CASE F.AGENCE -- Assuming F.AGENCE comes directly from SRC_COMMISSION_PRD
                        WHEN 'SAINT LOUIS' THEN 'Saint-Louis' WHEN 'RICHARD TOLL' THEN 'Saint-Louis'
                        WHEN 'KEDOUGOU' THEN 'Tamba' WHEN 'KOLDA' THEN 'Ziguinchor'
                        WHEN 'MATAM' THEN 'Tamba' WHEN 'ZIGUINCHOR' THEN 'Ziguinchor'
                        WHEN 'THIES' THEN 'Thies' WHEN 'FATICK' THEN 'Fatick'
                        WHEN 'PLATEAU' THEN 'Plateau' WHEN 'PIKINE' THEN 'Pikine'
                        WHEN 'MBACKE' THEN 'Diourbel' WHEN 'RUFISQUE' THEN 'Rufisque'
                        WHEN 'DAHRA' THEN 'Louga' WHEN 'TAMBA' THEN 'Tamba'
                        WHEN 'MEDINA' THEN 'Medina' WHEN 'LOUGA' THEN 'Louga'
                        WHEN 'DIOURBEL' THEN 'Diourbel' WHEN 'KAFFRINE' THEN 'Kaolack'
                        WHEN 'PARCELLES' THEN 'Parcelles' WHEN 'KAOLACK' THEN 'Kaolack'
                        WHEN 'GRAND DAKAR' THEN 'Grand Dakar' WHEN 'BAMBEY' THEN 'Diourbel'
                        WHEN 'GUEDIAWAYE' THEN 'Guediawaye' WHEN 'MBOUR' THEN 'Mbour'
                        ELSE F.AGENCE -- Keep original if no match (or set to NULL/default)
                    END AS AGENCE_TRANSFORMED,
                    F.AGENCE AS SHOPS, -- Use original AGENCE name for SHOPS
                    F.PRODUIT,
                    -- Ensure numeric fields handle the comma decimal separator if needed by Oracle target
                    -- If Oracle expects '.', conversion might be needed here or handled by Oracle NLS settings
                    REPLACE(F.CA_CAL, ',', '.'), REPLACE(F.CA_V, ',', '.'), REPLACE(F.REMB, ',', '.'),
                    REPLACE(F.COM_B, ',', '.'), REPLACE(F.ECART, ',', '.'), REPLACE(F.RET_F, ',', '.'),
                    REPLACE(F.DEC_AN, ',', '.'), REPLACE(F.ENG, ',', '.'), REPLACE(F.MUS, ',', '.'),
                    REPLACE(F.DEC_AC, ',', '.'), REPLACE(F.REGUL, ',', '.'), REPLACE(F.COM_N, ',', '.')
                FROM
                    OPTIWARETEMP.SRC_COMMISSION_PRD F
                JOIN
                    USER_DWHPR.DIM_TEMPS Te ON F.QUINZAINE = Te.JOUR -- Join condition using formatted date
                -- LEFT JOIN USER_DWHPR.DIM_CCS C ON AGENCE_TRANSFORMED = C.NOMCCS -- Join seems missing in original? Added if needed.
            """
            self.cursor_oracle_target.execute(insert_select_sql)
            self.logger.info(f"{self.cursor_oracle_target.rowcount} rows inserted into SIC_COMMISSION.")

            # 5. Commit transaction
            self.conn_oracle_target.commit()
            self.logger.info("Oracle transaction committed successfully.")
            return True

        except Exception as e:
            self.logger.error(f"Error during Oracle load process: {e}")
            # Rollback transaction in case of error
            try:
                self.conn_oracle_target.rollback()
                self.logger.info("Oracle transaction rolled back due to error.")
            except Exception as rb_err:
                self.logger.error(f"Failed to rollback Oracle transaction: {rb_err}")
            return False


# --- Main execution block ---
def run_commission():
    # Define keys used to fetch secrets/credentials
    env_variables_list = {
        "SQLSERVER_SOURCE_SERVER": "SQLSERVER_SOURCE_SERVER",
        "SQLSERVER_SOURCE_DATABASE": "SQLSERVER_SOURCE_DATABASE",
        "SQLSERVER_SOURCE_USERNAME": "SQLSERVER_SOURCE_USERNAME",
        "SQLSERVER_SOURCE_PASSWORD": "SQLSERVER_SOURCE_PASSWORD",
        "SQLSERVER_PROC_SERVER": "SQLSERVER_PROC_SERVER",
        "SQLSERVER_PROC_DATABASE": "SQLSERVER_PROC_DATABASE",
        "SQLSERVER_PROC_USERNAME": "SQLSERVER_PROC_USERNAME",
        "SQLSERVER_PROC_PASSWORD": "SQLSERVER_PROC_PASSWORD",
        "ORACLE_TARGET_HOST": "ORACLE_TARGET_HOST",
        "ORACLE_TARGET_PORT": "ORACLE_TARGET_PORT",
        "ORACLE_TARGET_SERVICE": "ORACLE_TARGET_SERVICE",
        "ORACLE_TARGET_USERNAME": "ORACLE_TARGET_USERNAME",
        "ORACLE_TARGET_PASSWORD": "ORACLE_TARGET_PASSWORD",
        "ORACLE_CLIENT_LIB_DIR": "ORACLE_CLIENT_LIB_DIR", # Optional client path
    }
    job = ExtractCommission(env_variables_list)
    job.process_extraction() # Use the overridden process method

if __name__ == "__main__":
    print(f"Script started at: {datetime.datetime.now()}")
    # Original script had a wait logic, uncomment if needed
    # wait_hour = 3600
    # def wait_until_day_is_valid():
    #     while True:
    #         current_day = datetime.datetime.now().day
    #         # Check if it's the 18th or the 3rd (adjust days as needed)
    #         if current_day == 18 or current_day == 3:
    #             print(f"Today is {current_day}, continuing the script.")
    #             break
    #         print(f"Today is {current_day}, waiting for the right day (3rd or 18th)... Sleeping for 1 hour.")
    #         time.sleep(wait_hour)
    # wait_until_day_is_valid()

    run_commission()
    print(f"Script finished at: {datetime.datetime.now()}")