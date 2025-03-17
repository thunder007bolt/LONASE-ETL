import pandas as pd, numpy as np
from base.loader import Loader
from utils.other_utils import load_env

load_env()


class ParifootOnlineLoad(Loader):
    def __init__(self):
        name = ('parifoot_online')
        log_file = 'logs/loader_parifoot_online.log'
        columns = [
            "id",
            "username",
            "balance",
            "total players",
            "total players date range",
            "sb bets no.",
            "sb stake",
            "sb closed stake",
            "sb wins no.",
            "sb wins",
            "sb ref no.",
            "sb refunds",
            "sb ggr",
            "cas.bets no.",
            "cas.stake",
            "cas.wins no.",
            "cas.wins",
            "cas.ref no.",
            "cas.refunds",
            "cas.ggr",
            "total ggr",
            "adjustments",
            "deposits",
            "financial deposits",
            "financial withdrawals",
            "transaction fee",
            "date"
        ]
        table_name = "[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET]"
        super().__init__(name, log_file, columns, table_name)

    def _convert_file_to_dataframe(self, file):
        df = pd.read_csv(file, sep=';', index_col=False)
        return df


def run_parifoot_online_loader():
    loader = ParifootOnlineLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_parifoot_online_loader()
