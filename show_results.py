"""
Zeigt eine vollständige Übersicht über alle Daten im AI Trading Bot
"""
import sqlite3
from datetime import datetime

DB_PATH = 'data/stock_data.db'

print("=" * 80)
print("AI STOCK TRADING BOT - DATENÜBERSICHT")
print("Mercedes-Benz Interview Demonstration")
print("=" * 80)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ============ TABELLEN ÜBERSICHT ============
    print("\n📋 DATENBANK-TABELLEN:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   ✅ {table}: {count} Einträge")
    
    # ============ AKTIENKURSE ============
    print("\n" + "=" * 80)
    print("📈 HISTORISCHE AKTIENKURSE")
    print("=" * 80)
    
    # Mercedes
    cursor.execute('''
        SELECT MIN(date), MAX(date), COUNT(*),
               AVG(close), MIN(close), MAX(close)
        FROM mercedes_prices
    ''')
    mb_stats = cursor.fetchone()
    if mb_stats[2] > 0:
        print(f"\n🚗 MERCEDES-BENZ (MBG.DE):")
        print(f"   Zeitraum: {mb_stats[0]} bis {mb_stats[1]}")
        print(f"   Datensätze: {mb_stats[2]}")
        print(f"   Ø Schlusskurs: €{mb_stats[3]:.2f}")
        print(f"   Min/Max: €{mb_stats[4]:.2f} / €{mb_stats[5]:.2f}")
    
    # DAX
    cursor.execute('''
        SELECT MIN(date), MAX(date), COUNT(*),
               AVG(close), MIN(close), MAX(close)
        FROM dax_prices
    ''')
    dax_stats = cursor.fetchone()
    if dax_stats[2] > 0:
        print(f"\n📊 DAX (^GDAXI):")
        print(f"   Zeitraum: {dax_stats[0]} bis {dax_stats[1]}")
        print(f"   Datensätze: {dax_stats[2]}")
        print(f"   Ø Schlusskurs: {dax_stats[3]:.2f}")
        print(f"   Min/Max: {dax_stats[4]:.2f} / {dax_stats[5]:.2f}")
    
    # ============ SENTIMENT-ANALYSE ============
    print("\n" + "=" * 80)
    print("🤖 KI SENTIMENT-ANALYSE")
    print("=" * 80)
    
    cursor.execute('SELECT COUNT(*) FROM news_sentiment')
    sentiment_count = cursor.fetchone()[0]
    
    if sentiment_count > 0:
        # Statistiken
        cursor.execute('''
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                MIN(sentiment_score) as min_sentiment,
                MAX(sentiment_score) as max_sentiment,
                COUNT(CASE WHEN recommendation = 'BUY' THEN 1 END) as buy_count,
                COUNT(CASE WHEN recommendation = 'HOLD' THEN 1 END) as hold_count,
                COUNT(CASE WHEN recommendation = 'SELL' THEN 1 END) as sell_count
            FROM news_sentiment
        ''')
        stats = cursor.fetchone()
        
        print(f"\n📊 STATISTIKEN:")
        print(f"   Analysierte News: {sentiment_count}")
        print(f"   Durchschn. Sentiment: {stats[0]:.2f} (Min: {stats[1]:.2f}, Max: {stats[2]:.2f})")
        print(f"   🟢 BUY: {stats[3]} | 🟡 HOLD: {stats[4]} | 🔴 SELL: {stats[5]}")
        
        # Gesamtstimmung
        if stats[0] > 0.3:
            overall = "🟢 POSITIV"
        elif stats[0] < -0.3:
            overall = "🔴 NEGATIV"
        else:
            overall = "🟡 NEUTRAL"
        print(f"   Gesamtstimmung: {overall}")
        
        # Top News
        print(f"\n📰 AKTUELLE NEWS-ANALYSEN:")
        print("-" * 80)
        cursor.execute('''
            SELECT headline, sentiment_score, recommendation, reason, date, publisher
            FROM news_sentiment
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        for i, row in enumerate(cursor.fetchall(), 1):
            sentiment_emoji = "🟢" if row[1] > 0.3 else "🔴" if row[1] < -0.3 else "🟡"
            rec_emoji = {"BUY": "📈", "HOLD": "⏸️", "SELL": "📉"}[row[2]]
            
            print(f"\n{i}. {sentiment_emoji} Score: {row[1]:+.2f} | {rec_emoji} {row[2]}")
            print(f"   {row[0][:75]}")
            print(f"   → {row[3]}")
            print(f"   📅 {row[4]} | 📰 {row[5]}")
    else:
        print("\n⚠️  Keine Sentiment-Daten vorhanden")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ DATENÜBERSICHT KOMPLETT")
    print("=" * 80 + "\n")
    
except Exception as e:
    print(f"\n❌ Fehler: {str(e)}")
