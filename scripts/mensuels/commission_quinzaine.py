### system ###
from base.database_extractor import DatabaseExtractor
import pandas as pd
import numpy as np
import datetime
delta_day = datetime.timedelta(days=1)

class ExtractCommissionQuinzaine(DatabaseExtractor):
    def __init__(self, env_variables_list):
        config_path = 'scripts/mensuels/commission_quinzaine.yml'
        super().__init__('commission_quinzaine', 'scripts/mensuels/logs/extract_commission_quinzaine.log', env_variables_list, config_path=config_path)
        self.annee = None
        self.mois = None
        self.jour = None
        
    def _set_date(self):
        """Calculates the specific date (jour, mois, annee) for the commission period."""
        """  Calcul de la p"""
        today = datetime.date.today()
        current_day = today.day


        if 1 <= current_day <= 15:
            # Second half of the previous month (16th to end of previous month)
            first_day_current_month = datetime.date(today.year, today.month, 1)
            prev_month_last_day = first_day_current_month - datetime.timedelta(days=1)
            start_date = datetime.date(prev_month_last_day.year, prev_month_last_day.month, 16)
            end_date = prev_month_last_day
            self.logger.info(f"Today is {current_day} (1-15), setting period to 2nd half of previous month: {start_date} to {end_date}")
        else:
            # First half of the current month (1st to 15th)
            start_date = datetime.date(today.year, today.month, 1)
            end_date = datetime.date(today.year, today.month, 15)
            self.logger.info(f"Today is {current_day} (16-end), setting period to 1st half of current month: {start_date} to {end_date}")

        #start_date = datetime.date(today.year, 2, 1)
        #end_date = datetime.date(today.year, 2, 15)
        self.start_date = start_date
        self.end_date = end_date
        self.annee = end_date.year
        self.mois = end_date.month
        self.jour = end_date.strftime("%d")
        self.logger.info(f"Commission period set to: Annee={self.annee}, Mois={self.mois:02d}, Jour={self.jour}")
    
    def _load_data_from_db(self):
        """Extracts commission data from the LONASE_SIC database."""
        if not self.conn_sql_server or not self.cursor_oracle:
            self.logger.error("Source SQL Server connection not available.")
            return None

        query = f"""
            SELECT *
            FROM [SRVBDD3\LONASE].[LONASE_SIC].[dbo].[commission_bi]
            WHERE year([QUINZAINE])= ?
              AND MONTH([QUINZAINE])= ?
              AND DAY([QUINZAINE]) = ?
        """
        try:
            self.logger.info(f"Extracting data for {self.annee}-{self.mois}-{self.jour} from source.")
            data = pd.read_sql_query(query, self.conn_sql_server, params=[self.annee, self.mois, self.jour])
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
              data['QUINZAINE'] = [datetime.datetime.strptime(str(i)[:10], "%d-%m-%Y").strftime("%d/%m/%Y") for i in data['QUINZAINE']]
              self.logger.info("QUINZAINE formatting complete.")
          else:
              self.logger.warning("Column 'QUINZAINE' not found for date formatting.")

          # Replace NaN with empty string
          self.logger.info("Replacing NaN values...")
          data = data.replace(np.nan, '')

          # Convert all fields to string and replace decimal point '.' with ','
          data = data.astype(str).applymap(lambda x: x.replace('.', ','))

          self.logger.info("Data transformation finished successfully.")
          return data
      except Exception as e:
          self.logger.error(f"Error during data transformation: {e}")
          return None
 
    def _load_data_to_oracle(self, data):
      """Loads the transformed data into the Oracle target database."""
      if not self._connect_oracle_target or not self.cursor_oracle:
          self.logger.error("Target Oracle connection not available.")
          return False
      if data is None or data.empty:
            self.logger.warning("No data provided to load into Oracle target.")
            return True 
      try:
          self.logger.info("Preparing data for Oracle insertion...")
          # Convert DataFrame records to list of tuples
          data_tuples = list(data.itertuples(index=False, name=None))
          self.logger.info(f"Converted {len(data_tuples)} rows to tuples.")

          # 1. Truncate temporary table
          self.logger.info("Truncating OPTIWARETEMP.SRC_COMMISSION_PRD...")
          self.cursor_oracle.execute("TRUNCATE TABLE OPTIWARETEMP.SRC_COMMISSION_PRD")
          self.logger.info("Truncate complete.")

          # 2. Insert data into temporary table
          self.logger.info(f"Inserting {len(data_tuples)} rows into OPTIWARETEMP.SRC_COMMISSION_PRD...")
          batch_size = 1000
          for i in range(0, len(data_tuples), batch_size):
              batch = data_tuples[i:i + batch_size]
              self.cursor_oracle.executemany("""
                  INSERT INTO OPTIWARETEMP.SRC_COMMISSION_PRD (
                  "QUINZAINE", "AGENCE", "PRODUIT", "IDENTIFIANT", "PRENOM", "NOM",
                  "CA_CAL", "CA_V", "REMB", "COM_B", "ECART", "RET_F", "DEC_AN",
                  "ENG", "MUS", "DEC_AC", "REGUL", "COM_N"
              ) VALUES (TO_DATE(:1, 'DD/MM/YYYY'), :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18)
              """, batch)
              self.conn_oracle.commit()
          # Check for batch errors
          errors = self.cursor_oracle.getbatcherrors()
          if errors:
              for error in errors:
                  self.logger.error(f"Error inserting row {error.offset}: {error.message}")
              self.conn_oracle.rollback() # Rollback on insertion errors
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
          self.cursor_oracle.execute(delete_sql)
          self.logger.info(f"{self.cursor_oracle.rowcount} rows deleted from SIC_COMMISSION.")
          
          self.logger.info("Inserting processed data into USER_DWHPR.SIC_COMMISSION...")
          insert_select_sql = """
                  INSERT INTO "USER_DWHPR"."SIC_COMMISSION" (IDENTIFIANT, IDTEMPS, AGENCE, SHOPS, PRODUIT, CA_CAL, CA_V, REMB, COM_B, ECART, RET_F, DEC_AN, ENG, MUS, DEC_AC, REGUL, COM_N)
                  SELECT F.IDENTIFIANT, Te.IDTEMPS, F.AGENCE, F.SHOPS, F.PRODUIT, F.CA_CAL, F.CA_V, F.REMB, F.COM_B, F.ECART, F.RET_F, F.DEC_AN, F.ENG, F.MUS, F.DEC_AC, F.REGUL, F.COM_N
                    FROM (
                              SELECT  QUINZAINE, CASE
                                      WHEN AGENCE LIKE 'SAINT LOUIS'	 THEN 	'Saint-Louis'
                                      WHEN AGENCE LIKE 'RICHARD TOLL'	 THEN 	'Saint-Louis'
                                      WHEN AGENCE LIKE 'KEDOUGOU'	 THEN 	'Tamba'
                                      WHEN AGENCE LIKE 'KOLDA'	 THEN 	'Ziguinchor'
                                      WHEN AGENCE LIKE 'MATAM'	 THEN 	'Tamba'
                                      WHEN AGENCE LIKE 'ZIGUINCHOR'	 THEN 	'Ziguinchor'
                                      WHEN AGENCE LIKE 'THIES'	 THEN 	'Thies'
                                      WHEN AGENCE LIKE 'FATICK'	 THEN 	'Fatick'
                                      WHEN AGENCE LIKE 'PLATEAU'	 THEN 	'Plateau'
                                      WHEN AGENCE LIKE 'PIKINE'	 THEN 	'Pikine'
                                      WHEN AGENCE LIKE 'MBACKE'	 THEN 	'Diourbel'
                                      WHEN AGENCE LIKE 'RUFISQUE'	 THEN 	'Rufisque'
                                      WHEN AGENCE LIKE 'DAHRA'	 THEN 	'Louga'
                                      WHEN AGENCE LIKE 'TAMBA'	 THEN 	'Tamba'
                                      WHEN AGENCE LIKE 'MEDINA'	 THEN 	'Medina'
                                      WHEN AGENCE LIKE 'LOUGA'	 THEN 	'Louga'
                                      WHEN AGENCE LIKE 'DIOURBEL'	 THEN 	'Diourbel'
                                      WHEN AGENCE LIKE 'KAFFRINE'	 THEN 	'Kaolack'
                                      WHEN AGENCE LIKE 'PARCELLES'	 THEN 	'Parcelles'
                                      WHEN AGENCE LIKE 'KAOLACK'	 THEN 	'Kaolack'
                                      WHEN AGENCE LIKE 'GRAND DAKAR'	 THEN 	'Grand Dakar'
                                      WHEN AGENCE LIKE 'BAMBEY'	 THEN 	'Diourbel'
                                      WHEN AGENCE LIKE 'GUEDIAWAYE'	 THEN 	'Guediawaye'
                                      WHEN upper(AGENCE) is NULL THEN 'Inconnu'
                                      WHEN AGENCE LIKE 'MBOUR'	 THEN 	'Mbour' END AGENCE
                                      ,AGENCE SHOPS, PRODUIT, IDENTIFIANT, PRENOM, NOM, CA_CAL,CA_V, REMB, COM_B, ECART, RET_F, DEC_AN, ENG, MUS, DEC_AC, REGUL, COM_N
                                FROM  OPTIWARETEMP.SRC_COMMISSION_PRD  
                          ) F, DIM_CCS C, DIM_TEMPS Te
                  WHERE F.AGENCE= C.NOMCCS
                    AND F.QUINZAINE= Te.JOUR
                    and upper(trim(produit)) not in ('ALR_HONORE_MS','BINGO','CASHCHRONO','CASINO','GITECH_MS','LOTO YAAKAR','LOTO_MS','LYAKAR_MS','MAX2CASH','MINISHOP',
  'PARIFOOT ONLINE LONASE','PARIFOOT_MS','PAYE_YAKAR','PLR_HONORE_MS','PYAKAR_MS','SOLIDICON','VIRTUEL_MS','VOUCHER','WINFOOT','ZONE_BETTING')
              """
          self.cursor_oracle.execute(insert_select_sql)
          self.logger.info(f"{self.cursor_oracle.rowcount} rows inserted into SIC_COMMISSION.")
    
          self.conn_oracle.commit()
          return True
        
      except Exception as e:
          self.logger.error(f"Error during Oracle load process: {e}")
          # Rollback transaction in case of error
          try:
              self.conn_oracle.rollback()
              self.logger.info("Oracle transaction rolled back due to error.")
          except Exception as rb_err:
              self.logger.error(f"Failed to rollback Oracle transaction: {rb_err}")
          return False

    def _call_sql_server_stored_procedure(self):
        """Calls the commission processing stored procedure."""
        if not self.conn_sql_server or not self.cursor_sql_server:
             self.logger.error("Processing SQL Server connection not available.")
             return False
        try:
            self.logger.info(f"Calling PROC_COMMISSION with Annee={self.annee}, Mois={self.mois}, Jour={self.jour}")
            self.conn_sql_server.execute("""
                EXEC [USER_DWHPR].[PROC_COMMISSION] @ANNEE = ?, @MOIS = ?, @QUINZAINE = ?
            """, (self.annee, self.mois, self.jour))
            self.cursor_sql_server.commit()
            self.logger.info("Successfully called PROC_COMMISSION_QUINZAINES.")
            return True
        except Exception as e:
            self.logger.error(f"Error calling PROC_COMMISSION: {e}")
            # Consider rolling back if necessary, though it's a SELECT call in the original context?
            # self.conn_sql_proc.rollback()
             
    def process_extraction(self):
        """Orchestrates the commission extraction, processing, and loading."""
        self.logger.info(f"Starting commission processing job: {self.name}")
        data = None
        success = False
        try:    
            self._set_date()
           
            # Establish all connections
            if not self._connect_oracle_target(): return
            if not self._connection_to_db(): return
            
            # Step 2: Extract data from source SQL Server
            data = self._load_data_from_db()
            if data is None or data.empty:
                self.logger.warning("No commission data found after initial SP call. Exiting.")
                return # Exit if no data
              
            # Step 4: Process/Transform data
            transformed_data = self._process_data(data)
            if transformed_data is None:
                self.logger.error("Data transformation failed. Aborting.")
                return
              
            # Step 5: Load data into target Oracle DB
            load_success = self._load_data_to_oracle(transformed_data)
            if not load_success:
                 self.logger.error("Loading data to Oracle failed.")
                 # Decide on rollback strategy if needed (e.g., if partial loads occurred)
            else:
                 self.logger.info("Commission data successfully processed and loaded.")
                 success = True
            
            # Step 6: Call Stored Procedure 
            try:
                self._call_sql_server_stored_procedure()
                print("test")
            except Exception as e:
                self.logger.error(f"Failed during SQL Server stored procedure call. Aborting.")
                return # Abort if SP call fails
                 
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred during commission processing: {e}")
            # Rollback Oracle transaction if applicable and connection exists
            if self.conn_oracle:
                 try:
                      self.conn_oracle.rollback()
                      self.logger.info("Oracle transaction rolled back due to error.")
                 except Exception as rb_err:
                      self.logger.error(f"Failed to rollback Oracle transaction: {rb_err}")
        finally:
            # Always close connections
            self._close_oracle_connection()
            self._close_sql_server_connection()
            self.logger.info(f"Commission processing job finished. Success: {success}")

def run_commission_quinzaine():
    env_variables_list = {
        "SERVER": "SQL_SERVER_HOST",
        "DATABASE": "SQL_SERVER_DB_NAME",
        "USERNAME": "SQL_SERVER_DB_USERNAME",
        "PASSWORD": "SQL_SERVER_DB_PASSWORD",
        "ORACLE_TARGET_HOST": "ORACLE_TARGET_HOST",
        "ORACLE_TARGET_PORT": "ORACLE_TARGET_PORT",
        "ORACLE_TARGET_SERVICE": "ORACLE_TARGET_SERVICE",
        "ORACLE_TARGET_USERNAME": "ORACLE_TARGET_USERNAME",
        "ORACLE_TARGET_PASSWORD": "ORACLE_TARGET_PASSWORD",
        "ORACLE_CLIENT_LIB_DIR": "ORACLE_CLIENT_LIB_DIR",
    }
    job = ExtractCommissionQuinzaine(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_commission_quinzaine()
