### system ###
from base.database_extractor import DatabaseExtractor
import pandas as pd
import datetime
from utils.date_utils import date_string_to_date
import os

class ExtractMinishop(DatabaseExtractor):
    def __init__(self, env_variables_list):
        super().__init__('minishop', 'logs/extract_minishop.log', env_variables_list)
        self.file_path = None

    def _load_data_from_db(self, start_date, end_date=None):
        self.logger.info("Récupération des données...")
        day = start_date.strftime("%Y-%m-%d")
        query_gac = f"""
            SELECT 
                CAST(DateSituation as Date) as DATE,
                E.Caption AS ETABLISSEMENT,
                J.Caption AS JEU,
                T.CodeTerminalVirtuel AS TERMINAL,
                V.CodeVendeur AS VENDEUR,
                H.MontantAVerser AS 'MONTANT A VERSER',
                H.MontantARembourser AS 'MONTANT A PAYER'
            FROM THPCCHISTORIQUESITUATION H, 
                TETABLISSEMENT E, 
                THPCPTERMINAL_VIRTUEL T, 
                THPCPVENDEUR V, 
                THPCPJEUX J 
            WHERE H.oidEtablissement = E.oid
                AND H.oidTerminal = T.oid 
                AND T.oidVendeur = V.oid 
                AND H.oidJeu = J.oid 
                AND J.Caption NOT LIKE 'SOLIDICON'
                AND V.CodeVendeur IN ('VD3692','VD3693','VD3694','VD3695','VD3696')
                 AND CAST(DateSituation as Date) = CAST('{day}' AS DATE)
            
            UNION ALL
            
            SELECT 
                CAST(DateSituation as Date)  AS DATE,
                E.Caption AS ETABLISSEMENT,
                J.Caption AS JEU,
                T.CodeTerminalVirtuel AS TERMINAL,
                V.CodeVendeur AS VENDEUR,
                H.MontantAVerser AS 'MONTANT A VERSER',
                H.MontantARembourser AS 'MONTANT A PAYER'
            FROM THPCCHISTORIQUESITUATION H, 
                TETABLISSEMENT E, 
                THPCPTERMINAL_VIRTUEL T, 
                THPCPVENDEUR V, 
                THPCPJEUX J 
            WHERE H.oidEtablissement = E.oid
                AND H.oidTerminal = T.oid 
                AND T.oidVendeur = V.oid 
                AND H.oidJeu = J.oid 
                AND J.Caption LIKE 'SOLIDICON'
                AND CAST(DateSituation as Date) = CAST('{day}' AS DATE)
            """

        data = pd.read_sql_query(query_gac, self.connexion)
        if len(data) == 0:
            self.logger.info("Aucune donnée")
        else:
            name = f"minishop_{start_date}.csv"
            self._save_file(data, type="csv", name=name, sep=";",index=False)

    def _set_date(self):
        date = datetime.date.today() - datetime.timedelta(days=2)
        self.start_date = date_string_to_date(os.getenv("start_date")) or self.config.get("start_date") or date
        self.end_date = date_string_to_date(os.getenv("end_date")) or self.config.get("end_date") or date


def run_minishop():
    env_variables_list = {
        "SERVER": "LONASE_DEF_SERVER",
        "DATABASE": "LONASE_DEF_DATABASE",
        "USERNAME": "LONASE_DEF_USERNAME",
        "PASSWORD": "LONASE_DEF_PASSWORD"
    }
    job = ExtractMinishop(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_minishop()
