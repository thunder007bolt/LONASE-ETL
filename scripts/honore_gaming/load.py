from base.csv_loader import CSVLoader
from utils.other_utils import load_env
load_env()

class HonoreGamingLoad(CSVLoader):
    def __init__(self):
        columns = [
            "reportdatetime",
            "ticketnumber",
            "state",
            "issuedatetime",
            "terminalid",
            "terminaldescription",
            "retailcategoryname",
            "retailcategorydescription",
            "agentid",
            "agentname",
            "paymentdatetime",
            "paymentterminalid",
            "paymentterminaldescription",
            "paymentretailcategoryname",
            "paymtretailcategorydescription",
            "paymentagentid",
            "paymentagentname",
            "canceldatetime",
            "cancelterminalid",
            "cancelterminaldescription",
            "cancelretailcategoryname",
            "cancelrtailcategorydescription",
            "cancelagentid",
            "cancelagentname",
            "canceladministratorlogin",
            "meetingdate",
            "meetingnumber",
            "racenumber",
            "betcategoryname",
            "bettype",
            "selection",
            "multivalue",
            "totalstake",
            "payableamount",
            "paidamount",
            "gamename"
        ]
        super().__init__(
            name='honore_gaming',
            log_file='logs/loader_honore_gaming.log',
            sql_columns=columns,
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ALR_HONORE_GAMING]",
            csv_sep=';',
            csv_encoding='utf-8'
        )
    
    def _load_datas(self, data):
        """Surcharge pour utiliser fast_executemany."""
        self.logger.info("Chargement des données dans la base...")
        insert_query = f"""
            INSERT INTO {self.sql_server_table_name} ({", ".join([f'[{col}]' for col in self.sql_server_columns])})
            VALUES
                ({", ".join(["?"] * len(self.sql_server_columns))})
        """
        if hasattr(self, 'sql_server_cursor') and self.sql_server_cursor:
            self.sql_server_cursor.fast_executemany = True
            self.sql_server_cursor.executemany(insert_query, data)
            self.sql_server_connexion.commit()
        else:
            # Fallback sur la méthode parente
            super()._load_datas(data)

def run_honore_gaming_loader():
    loader = HonoreGamingLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_honore_gaming_loader()