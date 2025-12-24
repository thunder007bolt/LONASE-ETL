from pathlib import Path
from base.simple_csv_transformer import SimpleCSVTransformer


class PmuLotsTransformer(SimpleCSVTransformer):
    def __init__(self, config_path=None, log_file=None):
        super().__init__(
            name='pmu_lots',
            log_file=log_file or 'logs/transformer_pmu_lots.log',
            csv_sep=';',
            csv_encoding='latin-1',
            add_date_columns=True,
            select_columns=['Joueur', 'Nombre de fois gagné', 'Montant', 'Type', 'Combinaison',
                          'Offre', 'produit', 'JOUR', 'ANNEE', 'MOIS'],
            archive_path=r"K:\DATA_FICHIERS\PMUSENEGAL\\",
            config_path=config_path
        )
    
    def _transform_file(self, file: Path, date=None):
        if date is None:
            date = self._get_file_date(file)
        
        # Utilise la logique de base
        super()._transform_file(file, date)
        
        # Note: L'encodage latin-1 est géré dans _read_csv et _save_to_archive


def run_pmu_lots_transformer(config_path=None, log_file=None):
    transformer = PmuLotsTransformer(config_path=config_path, log_file=log_file)
    transformer.process_transformation()

if __name__ == '__main__':
    run_pmu_lots_transformer()
