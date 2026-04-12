import requests
import pandas as pd
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "users.db")
API_URL = "https://randomuser.me/api/?results=20"

logger = logging.getLogger("etl_pipeline")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(str(BASE_DIR / "etl_pipeline.log"), maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Avoid duplicate handlers if the module gets imported multiple times
if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
    logger.addHandler(handler)


# NOTE: email primary key is created in the initial CREATE TABLE statement.
USERS_COLUMNS = {
    "gender": "TEXT",
    "first_name": "TEXT",
    "last_name": "TEXT",
    "nationality": "TEXT",
    "age": "INTEGER",
    "age_group": "TEXT",
    "email_domain": "TEXT",
    "dob_date": "TEXT",
    "loaded_at": "TEXT",
}


def ensure_users_table(conn: sqlite3.Connection) -> None:
    """Create/upgrade the `users` table to the expected schema."""
    cur = conn.cursor()

    # Ensure table exists with primary key
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY
        )
        """
    )

    # Discover current columns
    cur.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in cur.fetchall()}  # row[1] = column name

    # Add missing columns (idempotent)
    for col, col_type in USERS_COLUMNS.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")

    conn.commit()


@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def extract(existing_emails=None):
    logger.info("Starting extraction")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()["results"]
    df = pd.json_normalize(data)

    if existing_emails:
        before = len(df)
        df = df[~df["email"].isin(existing_emails)]
        logger.info(f"Filtered {before - len(df)} duplicates in extract")

    logger.info(f"Extracted {len(df)} rows")
    return df


def transform(df):
    logger.info("Starting transformation")

    if df.empty:
        return df

    df = df.copy()

    # flatten
    df["first_name"] = df["name.first"]
    df["last_name"] = df["name.last"]
    df["age"] = df["dob.age"]
    df["dob_date"] = df["dob.date"]

    # age_group
    df["age_group"] = pd.cut(
        df["age"],
        bins=[-1, 17, 30, 60, 200],
        labels=["Child", "Young Adult", "Adult", "Senior"],
    )

    # email domain
    df["email_domain"] = df["email"].str.split("@").str[1]

    # timestamp
    df["loaded_at"] = datetime.utcnow().isoformat()

    # remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["email"])
    logger.warning(f"Removed {before - len(df)} duplicate rows")

    # drop missing email
    df = df.dropna(subset=["email"])

    df = df[
        [
            "email",
            "gender",
            "first_name",
            "last_name",
            "nat",
            "age",
            "age_group",
            "email_domain",
            "dob_date",
            "loaded_at",
        ]
    ]

    df = df.rename(columns={"nat": "nationality"})

    logger.info(f"Transformed {len(df)} rows")
    return df


def get_existing_emails(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        ensure_users_table(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users")
        return {row[0] for row in cursor.fetchall()}
    finally:
        conn.close()


def load(df, db_path=DB_PATH):
    logger.info("Starting load")

    conn = sqlite3.connect(db_path)
    try:
        ensure_users_table(conn)

        before = conn.total_changes

        if not df.empty:
            df.to_sql("users", conn, if_exists="append", index=False, chunksize=100)

        conn.commit()

        loaded = conn.total_changes - before
        logger.info(f"Loaded {loaded} rows")
        return loaded
    finally:
        conn.close()


def run_etl():
    try:
        logger.info("ETL started")

        existing_emails = get_existing_emails()

        df = extract(existing_emails)
        df = transform(df)
        loaded = load(df)

        logger.info(f"ETL finished. Loaded {loaded} rows")

    except Exception as e:
        with open("alert.log", "a") as f:
            f.write(f"{datetime.utcnow()} ERROR: {str(e)}\n")

        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    run_etl()
