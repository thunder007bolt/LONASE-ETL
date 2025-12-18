import sys
sys.path.append("/")

from base.orchestrator import Orchestrator
from extract_monthly import run_afitech_commission_history_monthly
from transform import run_afitech_commission_history_transformer
from load import run_afitech_commission_history_loader

def run_afitech_commission_history_monthly_orchestrator():
    orchestrator = Orchestrator(
        name="afitech_commission_history_monthly",
        extractor=run_afitech_commission_history_monthly,
        transformer=run_afitech_commission_history_transformer,
        loader=run_afitech_commission_history_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_commission_history_monthly_orchestrator()