import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Prüfe ob Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_sentiment'")
if cursor.fetchone():
    print('✅ Tabelle news_sentiment existiert\n')
    
    # Anzahl Einträge
    cursor.execute('SELECT COUNT(*) FROM news_sentiment')
    count = cursor.fetchone()[0]
    print(f'📊 Anzahl Sentiment-Analysen: {count}\n')
    
    if count > 0:
        # Statistiken
        cursor.execute('''
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                COUNT(CASE WHEN recommendation = 'BUY' THEN 1 END) as buy_count,
                COUNT(CASE WHEN recommendation = 'HOLD' THEN 1 END) as hold_count,
                COUNT(CASE WHEN recommendation = 'SELL' THEN 1 END) as sell_count
            FROM news_sentiment
        ''')
        stats = cursor.fetchone()
        print(f'📈 Durchschnittliches Sentiment: {stats[0]:.2f}')
        print(f'🟢 BUY: {stats[1]} | 🟡 HOLD: {stats[2]} | 🔴 SELL: {stats[3]}\n')
        
        # Letzte 3 Analysen
        print('📰 Letzte 3 Sentiment-Analysen:\n')
        cursor.execute('''
            SELECT headline, sentiment_score, recommendation, reason 
            FROM news_sentiment 
            ORDER BY created_at DESC 
            LIMIT 3
        ''')
        
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f'{i}. Sentiment: {row[1]:+.2f} | {row[2]}')
            print(f'   {row[0][:70]}...')
            print(f'   → {row[3]}\n')
else:
    print('❌ Tabelle news_sentiment nicht gefunden')

conn.close()
