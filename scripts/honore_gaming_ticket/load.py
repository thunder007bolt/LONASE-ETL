import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env
load_env()

class HonoreGamingTicketLoad(Loader):
    def __init__(self):
        name = ('honore_gaming_ticket')
        log_file = 'logs/loader_honore_gaming_ticket.log'
        columns = [
            "year","month","jour","retailcategoryname","agence","terminaldescription","categorie_finale","gamename","bettype",
            "totalstake","payableamount","annulation","ticket_vendu","ticket_annule","ca","mintotalstake","paidamount"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PARI_HONOREGAMING]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_honore_gaming_ticket_loader():
    loader = HonoreGamingTicketLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_honore_gaming_ticket_loader()