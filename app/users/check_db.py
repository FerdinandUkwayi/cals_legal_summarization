import sqlite3
from db import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("PRAGMA table_info(users)")
print(cur.fetchall())
conn.close()