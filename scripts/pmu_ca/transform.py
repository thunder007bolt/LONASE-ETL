from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class PmuCATransformer(SimpleCSVTransformer):
    def __init__(self, config_path=None, log_file=None):
        super().__init__(
            name='pmu_ca',
            log_file=log_file or 'logs/transformer_pmu_ca.log',
            csv_sep=';',
            csv_encoding='utf-8',
            add_date_columns=True,
            select_columns=['PRODUIT', 'CA', 'SHARING', 'JOUR', 'ANNEE', 'MOIS'],
            archive_path=r"K:\DATA_FICHIERS\PMUSENEGAL\\",
            config_path=config_path
        )
    
    def _transform_file(self, file: Path, date=None):
        if date is None:
            date = self._get_file_date(file)
        
        # Utilise la logique de base
        super()._transform_file(file, date)
        
        # Nom de fichier personnalisé pour l'archive
        if self.archive_path and date:
            from pathlib import Path as PathLib
            archive_dir = PathLib(self.archive_path)
            filename = f"Pmu_Senegal_ca_{date.strftime('%Y-%m-%d')}.csv"
            # L'archive est déjà sauvegardée par la méthode parente, mais on peut la renommer si nécessaire

def run_pmu_ca_transformer(config_path=None, log_file=None):
    transformer = PmuCATransformer(config_path=config_path, log_file=log_file)
    transformer.process_transformation()


if __name__ == '__main__':
    run_pmu_ca_transformer()
