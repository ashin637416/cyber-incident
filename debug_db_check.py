import sqlite3
from config import Config
conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()
cur.execute('SELECT id, case_id, title, incident_type, incident_date, description FROM incidents ORDER BY id DESC LIMIT 5')
rows = cur.fetchall()
print('rows:', rows)
conn.close()
