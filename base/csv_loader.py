"""
Classe de base pour les loaders qui chargent des fichiers CSV.
Factorise la logique commune de chargement CSV.
"""
import pandas as pd
import numpy as np
from base.loader import Loader


class CSVLoader(Loader):
    """
    Classe de base pour les loaders CSV.
    Implémente _convert_file_to_dataframe par défaut pour les fichiers CSV.
    """
    
    def __init__(
        self,
        name,
        log_file,
        columns=None,
        table_name=None,
        sql_columns=None,
        sql_table_name=None,
        oracle_columns=None,
        oracle_table_name=None,
        config_path=None,
        env_variables_list=None,
        csv_sep=';',
        csv_encoding='utf-8',
        csv_dtype=None
    ):
        """
        Initialise le loader CSV.
        
        Args:
            name: Nom de la source
            log_file: Chemin du fichier de log
            columns: Colonnes SQL Server (déprécié, utiliser sql_columns)
            table_name: Nom de table SQL Server (déprécié, utiliser sql_table_name)
            sql_columns: Colonnes SQL Server
            sql_table_name: Nom de table SQL Server
            oracle_columns: Colonnes Oracle (optionnel)
            oracle_table_name: Nom de table Oracle (optionnel)
            config_path: Chemin de configuration (optionnel)
            env_variables_list: Liste des variables d'environnement (optionnel)
            csv_sep: Séparateur CSV (défaut: ';')
            csv_encoding: Encodage du fichier CSV (défaut: 'utf-8')
            csv_dtype: Type de données pour pandas (optionnel, ex: str pour tout en string)
        """
        super().__init__(
            name=name,
            log_file=log_file,
            columns=columns,
            table_name=table_name,
            sql_columns=sql_columns,
            sql_table_name=sql_table_name,
            oracle_columns=oracle_columns,
            oracle_table_name=oracle_table_name,
            config_path=config_path,
            env_variables_list=env_variables_list
        )
        self.csv_sep = csv_sep
        self.csv_encoding = csv_encoding
        self.csv_dtype = csv_dtype
    
    def _convert_file_to_dataframe(self, file):
        """
        Convertit un fichier CSV en DataFrame.
        
        Args:
            file: Chemin vers le fichier CSV
        
        Returns:
            pd.DataFrame: DataFrame avec les données du CSV
        """
        df = pd.read_csv(
            file,
            sep=self.csv_sep,
            index_col=False,
            encoding=self.csv_encoding,
            dtype=self.csv_dtype
        )
        df = df.replace(np.nan, '')
        return df

