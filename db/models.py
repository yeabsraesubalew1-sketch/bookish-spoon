import sqlite3
import os
from flask import session, abort
from config import DB_PATH, SQL_INIT_FILE

p = not os.path.exists(DB_PATH)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

try:
    with open(SQL_INIT_FILE, "r") as f:
        sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()

        print("Database initialized.")
except Exception as e:
    print(f"Error: {e}")
    exit(1)


cur = conn.cursor()


def is_session_set():
    try:
        session["user"]
    except KeyError:
        return False
    except Exception as e:
        print(f"Error: {e}")
        abort(500)
    else:
        return True