"""
Demo: AI Sentiment-Analyse mit Mock-Daten für Demonstration
Zeigt wie das System funktionieren würde mit echten AI-Analysen
"""
import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'data/stock_data.db'

# Simulierte News mit realistischen AI-Analysen
mock_news = [
    {
        'headline': 'Mercedes-Benz steigert Gewinn im dritten Quartal um 15 Prozent',
        'publisher': 'Reuters',
        'sentiment_score': 0.75,
        'recommendation': 'BUY',
        'reason': 'Starkes Gewinnwachstum deutet auf robuste Geschäftsentwicklung hin'
    },
    {
        'headline': 'Rückruf von 50.000 Mercedes-Fahrzeugen wegen Sicherheitsmängeln',
        'publisher': 'Bloomberg',
        'sentiment_score': -0.60,
        'recommendation': 'HOLD',
        'reason': 'Rückrufaktion belastet kurzfristig, aber Standard-Prozedere im Automobilsektor'
    },
    {
        'headline': 'Mercedes präsentiert neue E-Auto-Strategie mit 10 Milliarden Euro Investment',
        'publisher': 'Financial Times',
        'sentiment_score': 0.85,
        'recommendation': 'BUY',
        'reason': 'Massive Investition in E-Mobilität positioniert Mercedes als Marktführer'
    },
    {
        'headline': 'Analysten senken Kursziel für Mercedes-Benz Aktie um 5 Prozent',
        'publisher': 'Handelsblatt',
        'sentiment_score': -0.40,
        'recommendation': 'HOLD',
        'reason': 'Kurszielreduktion spiegelt vorsichtigere Markterwartungen wider'
    },
    {
        'headline': 'Mercedes gewinnt Großauftrag für Elektro-Lkw-Flotte in China',
        'publisher': 'Manager Magazin',
        'sentiment_score': 0.70,
        'recommendation': 'BUY',
        'reason': 'Expansion im chinesischen Markt eröffnet signifikantes Wachstumspotenzial'
    },
    {
        'headline': 'Branchenexperten warnen vor Überkapazitäten im Premiumsegment',
        'publisher': 'Wirtschaftswoche',
        'sentiment_score': -0.25,
        'recommendation': 'HOLD',
        'reason': 'Marktrisiken bestehen, aber Mercedes gut positioniert im Premiumbereich'
    },
    {
        'headline': 'Mercedes-Benz kündigt Dividendenerhöhung von 8 Prozent an',
        'publisher': 'Börsen-Zeitung',
        'sentiment_score': 0.65,
        'recommendation': 'BUY',
        'reason': 'Höhere Dividende signalisiert starkes Vertrauen des Managements'
    },
    {
        'headline': 'Neue Umweltauflagen könnten Mercedes Millionen kosten',
        'publisher': 'Frankfurter Allgemeine',
        'sentiment_score': -0.50,
        'recommendation': 'HOLD',
        'reason': 'Regulatorische Risiken belasten, aber branchenweit üblich'
    },
    {
        'headline': 'Mercedes übertrifft Absatzziele im Luxussegment um 20 Prozent',
        'publisher': 'Auto Motor Sport',
        'sentiment_score': 0.80,
        'recommendation': 'BUY',
        'reason': 'Überragende Performance im margenstärksten Segment'
    },
    {
        'headline': 'Partnerschaft mit Tech-Gigant für autonomes Fahren angekündigt',
        'publisher': 'TechCrunch',
        'sentiment_score': 0.90,
        'recommendation': 'BUY',
        'reason': 'Strategische Allianz beschleunigt Innovation und Wettbewerbsposition'
    }
]

print("=" * 80)
print("AI SENTIMENT-ANALYSE - DEMO MIT MOCK-DATEN")
print("Mercedes-Benz Stock Trading Bot")
print("=" * 80)

# Datenbank leeren
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('DELETE FROM news_sentiment')
conn.commit()

print("\n📰 IMPORTIERE MOCK-NEWS MIT AI-ANALYSEN...\n")

# News in Datenbank einfügen
for i, news in enumerate(mock_news, 1):
    cursor.execute('''
        INSERT INTO news_sentiment 
        (date, ticker, headline, publisher, sentiment_score, recommendation, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now() - timedelta(hours=i),
        'MBG.DE',
        news['headline'],
        news['publisher'],
        news['sentiment_score'],
        news['recommendation'],
        news['reason']
    ))
    
    emoji = "🟢" if news['sentiment_score'] > 0.3 else "🔴" if news['sentiment_score'] < -0.3 else "🟡"
    rec_emoji = {"BUY": "📈", "HOLD": "⏸️", "SELL": "📉"}[news['recommendation']]
    
    print(f"[{i}/10] {emoji} Sentiment: {news['sentiment_score']:+.2f} | {rec_emoji} {news['recommendation']}")
    print(f"       {news['headline'][:70]}...")
    print(f"       → {news['reason']}\n")

conn.commit()

# Statistiken berechnen
avg_sentiment = sum(n['sentiment_score'] for n in mock_news) / len(mock_news)
buy_count = sum(1 for n in mock_news if n['recommendation'] == 'BUY')
hold_count = sum(1 for n in mock_news if n['recommendation'] == 'HOLD')
sell_count = sum(1 for n in mock_news if n['recommendation'] == 'SELL')

print("=" * 80)
print("📊 KI SENTIMENT-ANALYSE ZUSAMMENFASSUNG")
print("=" * 80)

print(f"\n📊 STATISTIKEN:")
print(f"   Analysierte News: {len(mock_news)}")
print(f"   Durchschnittliches Sentiment: {avg_sentiment:.2f}")
print(f"   Empfehlungen: 🟢 BUY: {buy_count} | 🟡 HOLD: {hold_count} | 🔴 SELL: {sell_count}")

if avg_sentiment > 0.3:
    overall = "🟢 POSITIV"
elif avg_sentiment < -0.3:
    overall = "🔴 NEGATIV"
else:
    overall = "🟡 NEUTRAL"

print(f"   Gesamtstimmung: {overall}")

# Top und Flop News
print(f"\n📈 TOP 3 POSITIVSTE NEWS:")
top_news = sorted(mock_news, key=lambda x: x['sentiment_score'], reverse=True)[:3]
for i, news in enumerate(top_news, 1):
    print(f"{i}. {news['sentiment_score']:+.2f} - {news['headline'][:65]}...")

print(f"\n📉 TOP 3 NEGATIVSTE NEWS:")
bottom_news = sorted(mock_news, key=lambda x: x['sentiment_score'])[:3]
for i, news in enumerate(bottom_news, 1):
    print(f"{i}. {news['sentiment_score']:+.2f} - {news['headline'][:65]}...")

# Handelsempfehlung
print(f"\n💡 TRADING-EMPFEHLUNG:")
if avg_sentiment > 0.5:
    print("   🟢 STRONG BUY - Überwiegend positive Marktstimmung")
elif avg_sentiment > 0.2:
    print("   🟢 BUY - Leicht positive Tendenz")
elif avg_sentiment > -0.2:
    print("   🟡 HOLD - Neutrale Marktstimmung")
elif avg_sentiment > -0.5:
    print("   🔴 SELL - Leicht negative Tendenz")
else:
    print("   🔴 STRONG SELL - Überwiegend negative Marktstimmung")

conn.close()

print("\n" + "=" * 80)
print("✅ DEMO ERFOLGREICH ABGESCHLOSSEN!")
print("=" * 80)

print("\n💡 HINWEIS: Dies ist eine Demo mit simulierten AI-Analysen.")
print("   In der Produktion würde Claude AI echte News analysieren.")
