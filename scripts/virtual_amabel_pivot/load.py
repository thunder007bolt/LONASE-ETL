import pandas as pd
from base.loader import Loader
from utils.other_utils import load_env

load_env()

class VirtualAmabelLoad(Loader):
    def __init__(self):
        name = ('virtual_amabel_pivot')
        log_file = 'logs/loader_virtual_amabel_pivot.log'
        columns = [
            "start date",
            "end date",
            "client id",
            "client name",
            "client id (ext)",
            "entity id (ext)",
            "entity id",
            "entity name",
            "entity played id (ext)",
            "entity played",
            "entity played name",
            "currency",
            "playlist",
            "game",
            "market",
            "selection",
            "confirmed stake",
            "bet winnings",
            "paid out",
            "number of bets",
            "timezone",
            "combinations",
            "won bets",
            "bonus winnings",
            "local jackpot winnings",
            "local jackpot contribution",
            "local jackpot payout",
            "network jackpot winnings",
            "network jackpot contribution",
            "network jackpot payout",
            "cancelled stake",
            "played tickets",
            "cancelled tickets",
            "tags",
            "get rtp",
            "target balance",
            "jour",
            "annee",
            "mois"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_AMABEL]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df

def run_virtual_amabel_pivot_loader():
    loader = VirtualAmabelLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_virtual_amabel_pivot_loader()
