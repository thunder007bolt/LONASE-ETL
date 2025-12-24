from base.csv_loader import CSVLoader
from utils.other_utils import load_env

load_env()


class ParifootOnlineLoad(CSVLoader):
    def __init__(self):
        super().__init__(
            name='parifoot_online',
            log_file='logs/loader_parifoot_online.log',
            sql_columns=[
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
            ],
            sql_table_name="[DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET]",
            csv_sep=';',
            csv_encoding='utf-8',
            csv_dtype=str
        )


def run_parifoot_online_loader():
    loader = ParifootOnlineLoad()
    loader.process_loading()


if __name__ == "__main__":
    run_parifoot_online_loader()
