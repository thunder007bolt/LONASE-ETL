from pathlib import Path
import numpy as np
import pandas as pd
from base.tranformer import Transformer
from datetime import timedelta

delta = timedelta(days=1)

class HonoreGamingTicketTransformer(Transformer):
    def __init__(self):
        super().__init__('honore_gaming_ticket', 'logs/transformer_honore_gaming_ticket.log')
        agence_file = Path(self.config['agence_relative_file_path'])
        mise_file = Path(self.config['mise_relative_file_path'])
        self.mise_df = pd.read_csv(mise_file, sep=";", encoding="latin-1",index_col=False)
        self.agence_df = pd.read_csv(agence_file, sep=";", encoding="latin-1",index_col=False)

    def _transform_file(self, file: Path, date=None):
       date = self._get_file_date(file, reverse=True)
       prev_date = date
       cols_to_import = [
           "TerminalDescription",
           "RetailCategoryName",
           "ReportDateTime",
           "State",
           "MeetingDate",
           "BetType",
           "TotalStake",
           "GameName",
           "PayableAmount",
           "PaidAmount",
       ]

       # Lecture optimisée du CSV
       df = pd.read_csv(
           file,
           sep=";",
           encoding="latin-1",
           index_col=False,
           usecols=cols_to_import,
           dtype={"TotalStake": str, "PayableAmount": str, "PaidAmount": str},
       )

       # Fusions efficaces
       df = pd.merge(self.agence_df, df, on="RetailCategoryName", how="right")
       df = pd.merge(self.mise_df, df, on=["BetType", "GameName"], how="right")

       # Define conditions with contains
       conditions = [
           (df['GameName'].str.upper().str.contains('ALR')),  # GameName contains 'ALR'
           (df['GameName'].str.upper().str.contains('PLR')),  # GameName contains 'PLR'
           (df['GameName'].str.upper().str.contains('MCI')) & df['BetType'].str.upper().str.contains(
               '|'.join(['SIMPLE', 'COUPLE', 'TRIO'])),  # BetType contains any of these
           (df['GameName'].str.upper().str.contains('MCI')) & df['BetType'].str.upper().str.contains(
               '|'.join(['MULTI', 'QUINTE', 'QUARTE', 'TIERCE']))  # BetType contains any of these
       ]

       # Define corresponding outputs
       choices = ['ALR', 'PLR', 'PLR', 'ALR']

       # Apply the conditions to create a new column
       df['CATEGORIE_FINALE'] = np.select(conditions, choices, default='Unknown')
       # Conversion des types après fusion

       for col in ["TotalStake", "PayableAmount", "PaidAmount"]:
           df[col] = df[col].str.replace(",", ".").astype(float)

       df["MeetingDate"] = df["MeetingDate"].astype(str)
       date_str_1 = prev_date.strftime("%d/%m/%Y")
       date_str_2 = str(prev_date.date())

       # Filtrage optimisé
       df = df[df["MeetingDate"].str.contains(date_str_1, regex=True) | df["MeetingDate"].str.contains(date_str_2, regex=True)]

       # Calculs vectorisés
       df["ANNULATION"] = np.where(df["State"].str.lower() == "cancelled", df["TotalStake"], np.nan)
       df["TICKET_VENDU"] = df["TotalStake"] / df["MinTotalStake"]
       df["TICKET_ANNULE"] = df["ANNULATION"] / df["MinTotalStake"]
       df["CA"] = df["TotalStake"].fillna(0) - df["ANNULATION"].fillna(0)

       # Suppression des colonnes inutiles
       df = df.drop(["State", "ReportDateTime", "MeetingDate"], axis=1)
       df = df.fillna(0)

       # Préparation du fichier de sortie
       df["Year"] = (prev_date).strftime("%Y")
       df["Month"] = int((prev_date).strftime("%m"))
       df["JOUR"] = (prev_date).strftime("%d/%m/%Y")

       # Regroupement et écriture
       grouped_df = df.groupby(
           [
               "Year",
               "Month",
               "JOUR",
               "RetailCategoryName",
               "AGENCE",
               "TerminalDescription",
               "CATEGORIE_FINALE",
               "GameName",
               "BetType",
               "MinTotalStake",

           ]
       ).sum()

       grouped_df = grouped_df.reset_index()

       # Définir les colonnes à sélectionner
       colonnes = [
           'Year', 'Month', 'JOUR', 'RetailCategoryName', 'AGENCE',
           'TerminalDescription', 'CATEGORIE_FINALE', 'GameName',
           'BetType', 'TotalStake', 'PayableAmount', 'ANNULATION',
           'TICKET_VENDU', 'TICKET_ANNULE', 'CA', 'MinTotalStake', 'PaidAmount'
       ]

       # Sélectionner les colonnes
       grouped_df = grouped_df[colonnes]

       name = f"{self.name}_transformed_{prev_date.strftime('%Y-%m-%d')}.csv"

       self._save_file(file, grouped_df, name=name, type='csv', sep=";", encoding="latin-1", reverse=True, decimal=",", index=False)

def run_honore_gaming_ticket_transformer():
    transformer = HonoreGamingTicketTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_honore_gaming_ticket_transformer()

