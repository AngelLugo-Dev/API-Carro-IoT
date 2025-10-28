import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Any, Iterable, Optional
from .config import get_settings


settings = get_settings()


def get_connection():
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        cursorclass=DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.close()


def call_procedure(proc_name: str, args: Optional[Iterable[Any]] = None):
    args = tuple(args or [])
    with db_cursor() as cur:
        cur.callproc(proc_name, args)
        # Fetch all result sets if any
        results = cur.fetchall()
        # Consume remaining result sets to avoid "Unread result" errors
        while cur.nextset() is not None:
            pass
        return results


def execute(query: str, params: Optional[Iterable[Any]] = None):
    with db_cursor() as cur:
        cur.execute(query, params)
        if cur.description:  # has result set
            return cur.fetchall()
        return {"affected_rows": cur.rowcount, "lastrowid": cur.lastrowid}
