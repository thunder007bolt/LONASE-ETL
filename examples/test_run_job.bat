@echo off
REM Exemple de script Windows pour tester run_job.py avec différentes configurations

echo === Test 1: Job complet ===
set ETL_JOB_NAME=test_gitech_parifoot
set ETL_SOURCE_NAME=gitech_parifoot
set ETL_START_DATE=2025-01-15
set ETL_END_DATE=2025-01-15
python scripts/run_job.py

echo.
echo === Test 2: Transform et Load seulement ===
set ETL_JOB_NAME=test_transform_load
set ETL_SOURCE_NAME=gitech_parifoot
set ETL_SKIP_EXTRACT=true
python scripts/run_job.py

echo.
echo === Test 3: Mode debug ===
set ETL_JOB_NAME=test_debug
set ETL_SOURCE_NAME=gitech_parifoot
set ETL_DEBUG=true
set ETL_RETRY_COUNT=5
python scripts/run_job.py

echo.
echo === Test 4: Dry run ===
set ETL_JOB_NAME=test_dry_run
set ETL_SOURCE_NAME=gitech_parifoot
set ETL_DRY_RUN=true
python scripts/run_job.py

