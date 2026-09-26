"""
Demo: AI Sentiment-Analyse mit nur 3 News-Artikeln für schnellere Demonstration
"""
import os
import sqlite3
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Setup
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DB_PATH = 'data/stock_data.db'

# Test-News (simuliert, da yfinance manchmal keine News zurückgibt)
demo_headlines = [
    "Mercedes-Benz steigert Gewinn im dritten Quartal um 15 Prozent",
    "Rückruf von 50.000 Fahrzeugen wegen Sicherheitsproblemen bei Mercedes",
    "Mercedes-Benz präsentiert neue E-Auto-Strategie für 2027"
]

print("=" * 80)
print("AI SENTIMENT-ANALYSE - DEMO")
print("=" * 80)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

analyzed_news = []

for i, headline in enumerate(demo_headlines, 1):
    print(f"\n[{i}/3] Analysiere: {headline}")
    
    prompt = f"""Du bist ein professioneller Finanzanalyst. Analysiere diese News-Headline für Mercedes-Benz:

Headline: "{headline}"

Bewerte die Headline und gib deine Analyse im folgenden JSON-Format zurück:
{{
    "sentiment_score": <float zwischen -1.0 und +1.0>,
    "recommendation": "<BUY, HOLD oder SELL>",
    "reason": "<Einzeilige Begründung auf Deutsch>"
}}

Antworte NUR mit dem JSON-Objekt."""

    try:
        # Probiere verschiedene Modelle
        models = ["claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        
        message = None
        for model in models:
            try:
                message = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                break
            except:
                continue
        
        if not message:
            print("   ❌ Kein Modell verfügbar")
            continue
        
        # Parse response
        response_text = message.content[0].text.strip()
        
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        analysis = json.loads(response_text)
        
        # Validierung
        sentiment_score = round(float(analysis['sentiment_score']), 2)
        recommendation = analysis['recommendation'].upper()
        reason = analysis['reason']
        
        analyzed_news.append({
            'headline': headline,
            'sentiment_score': sentiment_score,
            'recommendation': recommendation,
            'reason': reason
        })
        
        emoji = "🟢" if sentiment_score > 0.3 else "🔴" if sentiment_score < -0.3 else "🟡"
        print(f"   {emoji} Sentiment: {sentiment_score:+.2f} | {recommendation}")
        print(f"   → {reason}")
        
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)[:50]}")

# Speichern in Datenbank
if analyzed_news:
    print("\n" + "=" * 80)
    print("Speichere Ergebnisse in Datenbank...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for news in analyzed_news:
        try:
            cursor.execute('''
                INSERT INTO news_sentiment 
                (date, ticker, headline, publisher, sentiment_score, recommendation, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                'MBG.DE',
                news['headline'],
                'Demo',
                news['sentiment_score'],
                news['recommendation'],
                news['reason']
            ))
        except:
            pass
    
    conn.commit()
    conn.close()
    
    # Statistiken
    avg_sentiment = sum(n['sentiment_score'] for n in analyzed_news) / len(analyzed_news)
    buy_count = sum(1 for n in analyzed_news if n['recommendation'] == 'BUY')
    hold_count = sum(1 for n in analyzed_news if n['recommendation'] == 'HOLD')
    sell_count = sum(1 for n in analyzed_news if n['recommendation'] == 'SELL')
    
    print("\n" + "=" * 80)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"Analysierte News: {len(analyzed_news)}")
    print(f"Durchschn. Sentiment: {avg_sentiment:.2f}")
    print(f"🟢 BUY: {buy_count} | 🟡 HOLD: {hold_count} | 🔴 SELL: {sell_count}")
    
    if avg_sentiment > 0.3:
        print("Gesamtstimmung: 🟢 POSITIV")
    elif avg_sentiment < -0.3:
        print("Gesamtstimmung: 🔴 NEGATIV")
    else:
        print("Gesamtstimmung: 🟡 NEUTRAL")
    
    print("\n✅ DEMO ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 80)
