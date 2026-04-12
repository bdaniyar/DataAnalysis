# ETL Pipeline Project

A small ETL pipeline that:
- extracts users from `randomuser.me`
- transforms/cleans fields
- loads results into SQLite (`lab11/users.db`)
- writes logs to `lab11/etl_pipeline.log`

## Requirements
- Python 3.11+
- macOS / zsh (commands below)

## Setup (venv + dependencies)
Run from the project root (`datanalysis/`).

### 1) Create a virtual environment
```bash
python3 -m venv lab11/venv
```

### 2) Activate the virtual environment
```bash
source lab11/venv/bin/activate
```

### 3) Install dependencies
```bash
python -m pip install -U pip
python -m pip install -r lab11/requirements.txt
```

### 4) Deactivate (optional)
```bash
deactivate
```

## Run ETL
You can run it from the root or from `lab11/`.

```bash
python lab11/etl_pipeline.py
```

Artifacts are created/updated here:
- Database: `lab11/users.db`
- Log file: `lab11/etl_pipeline.log`

## Run Scheduler
```bash
python lab11/scheduler.py
```

## Run Tests
From the root (`datanalysis/`):

```bash
pytest lab11/test_transform.py
```
