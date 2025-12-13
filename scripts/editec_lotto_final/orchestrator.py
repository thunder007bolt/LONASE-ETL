import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from transform import run_editec_lotto_final_transformer
from load import run_editec_lotto_final_loader

def run_editec_lotto_final_orchestrator():
    orchestrator = Orchestrator(
        name="editec_lotto_final",
        transformer=run_editec_lotto_final_transformer,
        loader=run_editec_lotto_final_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_editec_lotto_final_orchestrator()