import time
from etl_pipeline import run_etl
from datetime import datetime

for i in range(6):
    print(f"Running ETL at {datetime.now()}")
    run_etl()
    time.sleep(600)  # 10 минут