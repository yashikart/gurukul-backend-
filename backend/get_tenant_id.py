import sqlite3
conn = sqlite3.connect('gurukul.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM tenants WHERE name = 'demo.gurukul.blackholeinfiverse.com'")
row = cursor.fetchone()
if row:
    print(f"TENANT_ID:{row[0]}")
conn.close()
