from pathlib import Path
import pandas as pd
from base.simple_csv_transformer import SimpleCSVTransformer
from utils.date_utils import DATE_FORMAT_DISPLAY


class ParifootOnlineTransformer(SimpleCSVTransformer):
    def __init__(self):
        super().__init__(
            name='parifoot_online',
            log_file='logs/transformer_parifoot_online.log',
            csv_sep=',',  # Note: séparateur différent pour parifoot
            csv_encoding='utf-8',
            add_date_columns=False,  # Géré manuellement avec colonne 'date'
            select_columns=['Unnamed: 0', 'Username', 'Balance', 'Total Players', 'Total Players Date Range',
                          'SB Bets No.', 'SB Stake', 'SB Closed Stake', 'SB Wins No.', 'SB Wins',
                          'SB Ref No.', 'SB Refunds', 'SB GGR', 'Cas.Bets No.', 'Cas.Stake',
                          'Cas.Wins No.', 'Cas.Wins', 'Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR',
                          'Total GGR', 'Adjustments', 'Deposits', 'Financial Deposits',
                          'Financial Withdrawals', 'Transaction Fee', 'date'],
            archive_path=r"K:\DATA_FICHIERS\PARIFOOT_ONLINE\\"
        )
    
    def _transform_file(self, file: Path, date=None):
        if date is None:
            date = self._get_file_date(file)
        
        # Lecture CSV avec séparateur spécifique
        data = self._read_csv(file)
        
        # Ajout colonne date (format différent)
        data['date'] = date.strftime(DATE_FORMAT_DISPLAY)
        
        # Sélection colonnes
        if self.select_columns:
            data = data[self.select_columns]
        
        # Nettoyage
        data = self._clean_dataframe(data)
        
        # Archive
        if self.archive_path:
            self._save_to_archive(data, date, filename_prefix="ParifootOnline")
        
        # Sauvegarde
        self._save_file(file=file, data=data, type="csv", index=False, sep=';', encoding='utf8')



def run_parifoot_online_transformer():
    transformer = ParifootOnlineTransformer()
    transformer.process_transformation()


if __name__ == '__main__':
    run_parifoot_online_transformer()
