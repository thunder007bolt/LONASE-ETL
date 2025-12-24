"""
Utilitaires pour la manipulation de DataFrames pandas.
Centralise les opérations communes sur les DataFrames.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any


def read_csv_safe(file: Path, sep: str = ';', encoding: str = 'utf-8', 
                  index_col: bool = False, dtype: Optional[Dict[str, Any]] = None,
                  **kwargs) -> pd.DataFrame:
    """
    Lit un fichier CSV avec gestion d'erreurs standardisée.
    
    Args:
        file: Chemin vers le fichier CSV
        sep: Séparateur CSV (défaut: ';')
        encoding: Encodage du fichier (défaut: 'utf-8')
        index_col: Si True, utilise la première colonne comme index
        dtype: Types de données pour les colonnes (optionnel)
        **kwargs: Arguments supplémentaires pour pd.read_csv
    
    Returns:
        pd.DataFrame: DataFrame avec les données
    
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        pd.errors.EmptyDataError: Si le fichier est vide
        Exception: Autres erreurs de lecture
    """
    try:
        df = pd.read_csv(
            file,
            sep=sep,
            encoding=encoding,
            index_col=index_col,
            dtype=dtype,
            **kwargs
        )
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier non trouvé : {file}")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"Fichier vide : {file}")
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture de {file}: {e}")


def clean_dataframe(df: pd.DataFrame, replace_nan: Any = '', to_string: bool = False) -> pd.DataFrame:
    """
    Nettoie un DataFrame : remplace NaN et convertit en string si demandé.
    
    Args:
        df: DataFrame à nettoyer
        replace_nan: Valeur de remplacement pour NaN (défaut: '')
        to_string: Si True, convertit toutes les colonnes en string
    
    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    df = df.replace(np.nan, replace_nan)
    if to_string:
        df = df.astype(str)
    return df


def select_columns(df: pd.DataFrame, columns: List[str], 
                   fill_missing: bool = True, fill_value: Any = '') -> pd.DataFrame:
    """
    Sélectionne des colonnes d'un DataFrame.
    
    Args:
        df: DataFrame source
        columns: Liste des colonnes à sélectionner
        fill_missing: Si True, crée les colonnes manquantes avec fill_value
        fill_value: Valeur pour les colonnes manquantes (défaut: '')
    
    Returns:
        pd.DataFrame: DataFrame avec colonnes sélectionnées
    """
    if fill_missing:
        missing_cols = [col for col in columns if col not in df.columns]
        for col in missing_cols:
            df[col] = fill_value
    
    return df[columns]

