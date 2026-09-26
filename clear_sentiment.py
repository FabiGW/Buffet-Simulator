import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

cursor.execute('DELETE FROM news_sentiment')
conn.commit()

print('✅ news_sentiment Tabelle geleert')

cursor.execute('SELECT COUNT(*) FROM news_sentiment')
print(f'Aktuelle Einträge: {cursor.fetchone()[0]}')

conn.close()
