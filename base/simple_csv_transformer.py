"""
Classe de base pour les transformers CSV simples.
Factorise la logique commune de transformation de fichiers CSV simples.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from base.transformer import Transformer
from utils.date_utils import DATE_FORMAT_DISPLAY, DATE_FORMAT_STORAGE


class SimpleCSVTransformer(Transformer):
    """
    Classe de base pour les transformers CSV simples.
    Gère la lecture CSV, l'ajout de colonnes de date, le nettoyage et la sauvegarde.
    """
    
    def __init__(self, name, log_file, 
                 csv_sep=';', 
                 csv_encoding='utf-8',
                 add_date_columns=False,
                 select_columns=None,
                 archive_path=None,
                 config_path=None):
        """
        Initialise le transformer CSV simple.
        
        Args:
            name: Nom de la source
            log_file: Chemin du fichier de log
            csv_sep: Séparateur CSV (défaut: ';')
            csv_encoding: Encodage du fichier CSV (défaut: 'utf-8')
            add_date_columns: Si True, ajoute JOUR, ANNEE, MOIS (défaut: False)
            select_columns: Liste de colonnes à sélectionner (optionnel)
            archive_path: Chemin pour sauvegarder l'archive (optionnel)
            config_path: Chemin de configuration (optionnel)
        """
        super().__init__(name, log_file, config_path=config_path)
        self.csv_sep = csv_sep
        self.csv_encoding = csv_encoding
        self.add_date_columns = add_date_columns
        self.select_columns = select_columns
        self.archive_path = archive_path
    
    def _read_csv(self, file: Path) -> pd.DataFrame:
        """
        Lit un fichier CSV avec gestion d'erreurs.
        
        Args:
            file: Chemin vers le fichier CSV
        
        Returns:
            pd.DataFrame: DataFrame avec les données
        
        Raises:
            Exception: Si la lecture échoue
        """
        try:
            data = pd.read_csv(
                file, 
                sep=self.csv_sep, 
                index_col=False,
                encoding=self.csv_encoding
            )
            return data
        except Exception as e:
            self.set_error(file.name)
            self.logger.error(f"Erreur lors de la lecture de {file.name} : {e}")
            raise
    
    def _add_date_columns(self, data: pd.DataFrame, date) -> pd.DataFrame:
        """
        Ajoute les colonnes JOUR, ANNEE, MOIS au DataFrame.
        
        Args:
            data: DataFrame à modifier
            date: Objet date à utiliser
        
        Returns:
            pd.DataFrame: DataFrame avec colonnes de date ajoutées
        """
        if date is None:
            date = self._get_file_date(data)
        
        data["JOUR"] = str(date.strftime(DATE_FORMAT_DISPLAY))
        data["ANNEE"] = str(date.strftime("%Y"))
        data["MOIS"] = str(date.strftime("%m"))
        return data
    
    def _clean_dataframe(self, data: pd.DataFrame, to_string: bool = True) -> pd.DataFrame:
        """
        Nettoie le DataFrame : remplace NaN et convertit en string si demandé.
        
        Args:
            data: DataFrame à nettoyer
            to_string: Si True, convertit toutes les colonnes en string
        
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        data = data.replace(np.nan, '')
        if to_string:
            data = data.astype(str)
        return data
    
    def _save_to_archive(self, data: pd.DataFrame, date, filename_prefix: str = None):
        """
        Sauvegarde le DataFrame dans le répertoire d'archive.
        
        Args:
            data: DataFrame à sauvegarder
            date: Date pour le nom de fichier
            filename_prefix: Préfixe pour le nom de fichier (optionnel)
        """
        if not self.archive_path:
            return
        
        from pathlib import Path as PathLib
        archive_dir = PathLib(self.archive_path)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        prefix = filename_prefix or self.name
        filename = f"{prefix} {date.strftime(DATE_FORMAT_STORAGE)}.csv"
        filepath = archive_dir / filename
        
        data.to_csv(
            filepath,
            index=False,
            sep=self.csv_sep,
            encoding=self.csv_encoding
        )
        self.logger.info(f"Archive sauvegardée : {filepath}")
    
    def _transform_file(self, file: Path, date=None):
        """
        Traite un fichier CSV simple.
        Les transformers spécifiques peuvent surcharger cette méthode pour ajouter
        de la logique personnalisée avant ou après les étapes standard.
        """
        self.logger.info(f"Traitement du fichier : {file.name}")
        
        # Lecture CSV
        data = self._read_csv(file)
        
        # Ajout colonnes date si nécessaire
        if self.add_date_columns:
            if date is None:
                date = self._get_file_date(file)
            data = self._add_date_columns(data, date)
        
        # Sélection colonnes si nécessaire
        if self.select_columns:
            data = data[self.select_columns]
        
        # Nettoyage
        data = self._clean_dataframe(data)
        
        # Archive si nécessaire
        if self.archive_path and date:
            self._save_to_archive(data, date)
        
        # Sauvegarde via la méthode parente
        self._save_file(
            file=file, 
            data=data, 
            type="csv", 
            sep=self.csv_sep,
            encoding=self.csv_encoding,
            index=False
        )

