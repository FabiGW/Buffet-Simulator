"""Verifiziert die Trading Signals Tabelle"""
import sqlite3

conn = sqlite3.connect('data/stock_data.db')
c = conn.cursor()

# Tabellen anzeigen
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('📋 Tabellen:', [row[0] for row in c.fetchall()])

# Trading Signals Count
c.execute('SELECT COUNT(*) FROM trading_signals')
print(f'\n✅ Trading Signals: {c.fetchone()[0]} Einträge')

# Neueste 5 Signale
print('\n📊 NEUESTE 5 HANDELSSIGNALE:')
print('=' * 80)
c.execute('''
    SELECT datum, signal, aktueller_preis, sma20, sentiment_score, begruendung
    FROM trading_signals
    ORDER BY datum DESC
    LIMIT 5
''')

for row in c.fetchall():
    emoji = "🟢" if row[1] == "BUY" else "🔴" if row[1] == "SELL" else "🟡"
    print(f"\n{emoji} {row[0]}: {row[1]}")
    print(f"   Preis: €{row[2]:.2f} | SMA20: €{row[3]:.2f} | Sentiment: {row[4]:+.2f}")
    print(f"   → {row[5]}")

conn.close()
print('\n' + '=' * 80)
print('✅ Verifizierung abgeschlossen!')
