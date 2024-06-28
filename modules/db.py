# Подключение к базе данных SQLite
import sqlite3

from config import app_config

conn = sqlite3.connect(app_config.db_path, check_same_thread=False)
cursor = conn.cursor()


# Export the connection and cursor
def get_db_connection() -> sqlite3.Connection:
    return conn


def get_db_cursor() -> sqlite3.Cursor:
    return cursor
