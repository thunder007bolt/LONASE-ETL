#!/bin/bash
# Exemple de script pour tester run_job.py avec différentes configurations

echo "=== Test 1: Job complet ==="
export ETL_JOB_NAME=test_gitech_parifoot
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_START_DATE=2025-01-15
export ETL_END_DATE=2025-01-15
python scripts/run_job.py

echo ""
echo "=== Test 2: Transform et Load seulement ==="
export ETL_JOB_NAME=test_transform_load
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_SKIP_EXTRACT=true
python scripts/run_job.py

echo ""
echo "=== Test 3: Mode debug ==="
export ETL_JOB_NAME=test_debug
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DEBUG=true
export ETL_RETRY_COUNT=5
python scripts/run_job.py

echo ""
echo "=== Test 4: Dry run ==="
export ETL_JOB_NAME=test_dry_run
export ETL_SOURCE_NAME=gitech_parifoot
export ETL_DRY_RUN=true
python scripts/run_job.py

