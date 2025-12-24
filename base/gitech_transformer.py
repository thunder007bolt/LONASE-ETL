"""
Classe de base pour les transformers Gitech.
Factorise la logique commune de transformation des fichiers Gitech.
"""
import re
from pathlib import Path
import pandas as pd
from base.transformer import Transformer
from utils.excel_utils import convert_xls_to_xlsx
from utils.data_cleaning_utils import clean_numeric_value


class GitechBaseTransformer(Transformer):
    """
    Classe de base pour les transformers Gitech.
    Gère la conversion XLS->XLSX, l'extraction de date, et le nettoyage des données.
    """
    
    def __init__(self, name: str, log_file: str, skiprows: int = 6, date_pattern: str = None):
        """
        Initialise le transformer Gitech.
        
        Args:
            name: Nom de la source (ex: 'gitech_lotto')
            log_file: Chemin du fichier de log
            skiprows: Nombre de lignes à sauter lors de la lecture Excel (défaut: 6)
            date_pattern: Pattern regex pour extraire la date (optionnel)
        """
        super().__init__(name, log_file)
        self.skiprows = skiprows
        self.date_pattern = date_pattern or r"date\s+de\s+début\s+de\s+la\s+vente\s*:\s*(\d{2}/\d{2}/\d{4})"
    
    def convert_xls_to_xlsx(self, xls_file: Path) -> Path:
        """
        Convertit un fichier XLS en XLSX.
        
        Args:
            xls_file: Chemin vers le fichier XLS
        
        Returns:
            Path: Chemin vers le fichier XLSX créé
        """
        return convert_xls_to_xlsx(xls_file, self.logger)
    
    def extract_date_from_file(self, xlsx_file: Path) -> str:
        """
        Extrait la date contenue dans le fichier XLSX.
        
        Args:
            xlsx_file: Chemin vers le fichier XLSX
        
        Returns:
            str: Date au format DD/MM/YYYY
        
        Raises:
            ValueError: Si la date n'est pas trouvée
        """
        self.logger.info(f"Extraction de la date à partir du fichier {xlsx_file.name}")
        df = pd.read_excel(xlsx_file, nrows=6)  # Lecture des 6 premières lignes
        
        for idx, row in df.iterrows():
            cell_str = str(row).lower()
            match = re.search(self.date_pattern, cell_str)
            if match:
                return match.group(1)
        raise ValueError("Date non trouvée dans le fichier.")
    
    def process_numeric_column(self, value):
        """
        Nettoie et convertit une valeur numérique.
        
        Args:
            value: Valeur à nettoyer
        
        Returns:
            int: Valeur numérique nettoyée
        """
        return clean_numeric_value(value)
    
    def _prepare_excel_file(self, file: Path) -> Path:
        """
        Prépare le fichier Excel (conversion XLS->XLSX si nécessaire).
        
        Args:
            file: Fichier source
        
        Returns:
            Path: Fichier XLSX prêt à être lu
        
        Raises:
            Exception: Si la conversion échoue
        """
        if file.suffix.lower() == ".xls":
            xlsx_file = self.convert_xls_to_xlsx(file)
            self.logger.info(f"Conversion de {file.name} en {xlsx_file.name} réussie.")
            return xlsx_file
        elif file.suffix.lower() == ".xlsx":
            return file
        else:
            raise Exception(f"Type de fichier non géré : {file.name}")
    
    def _read_excel_data(self, xlsx_file: Path) -> pd.DataFrame:
        """
        Lit les données Excel en sautant les lignes d'en-tête.
        
        Args:
            xlsx_file: Fichier XLSX à lire
        
        Returns:
            pd.DataFrame: DataFrame avec les données
        """
        return pd.read_excel(xlsx_file, skiprows=range(0, self.skiprows))
    
    def _apply_common_cleaning(self, data: pd.DataFrame, col_mapping: dict, 
                                exclude_patterns: list = None, 
                                exclude_values: dict = None) -> pd.DataFrame:
        """
        Applique le nettoyage commun aux données Gitech.
        
        Args:
            data: DataFrame à nettoyer
            col_mapping: Mapping des colonnes à renommer
            exclude_patterns: Liste de patterns regex pour exclure des lignes (ex: ['^YAKAAR\(', '^Parifoot\('])
            exclude_values: Dict avec colonnes et valeurs à exclure (ex: {'Date vente': ['Total', 'montant global']})
        
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        # Renommage des colonnes
        data.rename(columns=col_mapping, inplace=True)
        
        # Exclusion par valeurs
        if exclude_values:
            for col, values in exclude_values.items():
                if col in data.columns:
                    data = data[~data[col].isin(values)]
        
        # Exclusion par patterns regex
        if exclude_patterns:
            for pattern in exclude_patterns:
                if 'Agences' in data.columns:
                    mask = data['Agences'].astype(str).str.match(pattern, na=False)
                    data = data[~mask]
        
        # Exclusion des lignes où Agences et Operateur sont tous deux NaN
        if 'Agences' in data.columns and 'Operateur' in data.columns:
            data = data[~(data['Agences'].isna() & data['Operateur'].isna())]
        
        return data
    
    def _process_numeric_columns(self, data: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
        """
        Nettoie les colonnes numériques.
        
        Args:
            data: DataFrame à traiter
            numeric_cols: Liste des colonnes numériques à nettoyer
        
        Returns:
            pd.DataFrame: DataFrame avec colonnes numériques nettoyées
        """
        for col in numeric_cols:
            if col in data.columns:
                data[col] = data[col].apply(self.process_numeric_column)
        return data

