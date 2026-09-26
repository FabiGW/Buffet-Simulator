import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Tabellen anzeigen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tabellen:', [row[0] for row in cursor.fetchall()])

# Mercedes Einträge
cursor.execute('SELECT COUNT(*) FROM mercedes_prices')
print('Mercedes Einträge:', cursor.fetchone()[0])

# DAX Einträge
cursor.execute('SELECT COUNT(*) FROM dax_prices')
print('DAX Einträge:', cursor.fetchone()[0])

conn.close()
print('\n✅ Datenbank erfolgreich verifiziert!')
