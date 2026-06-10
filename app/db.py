import json
from contextlib import contextmanager
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL


@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def now_utc():
    return datetime.now(timezone.utc)


def json_dumps(value):
    return json.dumps(value, ensure_ascii=False, default=str)


def count_table(table_name):
    with get_conn() as conn:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
        return row["c"]
