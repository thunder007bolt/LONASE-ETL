import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class HonoreGamingLoad(Loader):
    def __init__(self):
        name = ('honore_gaming')
        log_file = 'logs/loader_honore_gaming.log'
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
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_ALR_HONORE_GAMING]"
        super().__init__(name, log_file, columns, table_name)

    def _load_datas(self, data):
        self.logger.info("Chargement des données dans la base...")
        insert_query = f"""
            INSERT INTO {self.table_name} ({", ".join([f'[{col}]' for col in self.columns])})
            VALUES
                ({", ".join(["?"] * len(self.columns))})
        """
        self.cursor.fast_executemany = True
        self.cursor.executemany(insert_query, data)
        self.connexion.commit()

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_honore_gaming_loader():
    loader = HonoreGamingLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_honore_gaming_loader()