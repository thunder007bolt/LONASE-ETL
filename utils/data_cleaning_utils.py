"""
Utilitaires pour le nettoyage et la transformation de données.
"""
import pandas as pd


def clean_numeric_value(value) -> int:
    """
    Nettoie et convertit une valeur lue depuis une colonne numérique.
    
    - Suppression des espaces insécables (non-breaking spaces)
    - Si une virgule est présente, suppression des zéros finaux et de la virgule
    - Conversion en entier (les erreurs produisent un 0)
    
    Args:
        value: Valeur à nettoyer (peut être str, int, float, etc.)
    
    Returns:
        int: Valeur numérique nettoyée, 0 en cas d'erreur
    """
    value_str = str(value).replace(u'\xa0', '')  # Supprime les espaces insécables
    
    if ',' in value_str:
        # Supprime les zéros finaux et la virgule (ex: "1,00" -> "1")
        value_str = value_str.rstrip('00').replace(',', '')
    
    try:
        numeric_value = pd.to_numeric(value_str, errors='coerce')
        if pd.isna(numeric_value):
            return 0
        return int(numeric_value)
    except Exception:
        return 0


def clean_numeric_column(series: pd.Series) -> pd.Series:
    """
    Nettoie une colonne entière d'un DataFrame.
    
    Args:
        series: Série pandas à nettoyer
    
    Returns:
        pd.Series: Série nettoyée avec des valeurs entières
    """
    return series.apply(clean_numeric_value)


def format_gross_payout(series: pd.Series) -> pd.Series:
    """
    Formate une colonne 'Gross Payout' : float arrondi à 2 décimales puis string.
    
    Args:
        series: Série pandas avec les valeurs Gross Payout
    
    Returns:
        pd.Series: Série formatée en string avec 2 décimales
    """
    return series.astype(float).round(2).astype(str)

