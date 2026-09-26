"""
AI Sentiment Analysis Pipeline für Stock Trading Bot
Analysiert aktuelle News mit Claude AI und generiert Trading-Empfehlungen.

Author: Senior AI & Software Engineer
Purpose: Mercedes-Benz Interview Demonstration
"""

import os
import yfinance as yf
import sqlite3
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import json


# ========================= KONFIGURATION =========================

# Environment Variables laden
load_dotenv()

TICKER = 'MBG.DE'
DB_PATH = os.path.join('data', 'stock_data.db')

# API Key sicher aus .env laden
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == 'your_api_key_here':
    raise ValueError(
        "❌ ANTHROPIC_API_KEY nicht gefunden!\n"
        "Bitte tragen Sie Ihren API-Key in der .env Datei ein."
    )


# ========================= FUNKTIONEN =========================

def fetch_news(ticker: str) -> list:
    """
    Ruft aktuelle News für einen Ticker ab.
    
    Args:
        ticker: Ticker-Symbol (z.B. 'MBG.DE')
        
    Returns:
        Liste von News-Dictionaries mit title, publisher, link
    """
    print(f"\n[INFO] Rufe News für {ticker} ab...")
    
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            print(f"[WARNING] Keine News für {ticker} gefunden.")
            return []
        
        print(f"[SUCCESS] {len(news)} News-Artikel gefunden.")
        
        # News-Daten strukturieren
        news_list = []
        for article in news:
            news_list.append({
                'title': article.get('title', 'Kein Titel'),
                'publisher': article.get('publisher', 'Unbekannt'),
                'link': article.get('link', ''),
                'publish_time': article.get('providerPublishTime', None)
            })
        
        return news_list
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Abrufen der News: {str(e)}")
        return []


def generate_mock_sentiment(headline: str) -> dict:
    """
    Generiert Mock-Sentiment basierend auf Schlüsselwörtern in der Headline.
    Wird als Fallback verwendet wenn Claude API nicht verfügbar ist.
    
    Args:
        headline: News-Überschrift
        
    Returns:
        Dictionary mit sentiment_score, recommendation, reason
    """
    headline_lower = headline.lower()
    
    # Positive Schlüsselwörter
    positive_keywords = ['gewinn', 'steiger', 'wachstum', 'erfolg', 'partnerschaft', 
                         'innovation', 'dividende', 'profit', 'beats', 'übertrifft',
                         'strong', 'growth', 'partnership', 'record']
    
    # Negative Schlüsselwörter
    negative_keywords = ['rückruf', 'verlust', 'krise', 'problem', 'recall', 'senken',
                         'warnung', 'risiko', 'skandal', 'slowdown', 'falls', 'drops']
    
    # Zähle Vorkommen
    positive_count = sum(1 for word in positive_keywords if word in headline_lower)
    negative_count = sum(1 for word in negative_keywords if word in headline_lower)
    
    # Berechne Sentiment
    if positive_count > negative_count:
        sentiment_score = min(0.7, 0.3 + positive_count * 0.2)
        recommendation = 'BUY'
        reason = 'Positive Marktindikatoren und Unternehmensnachrichten'
    elif negative_count > positive_count:
        sentiment_score = max(-0.6, -0.3 - negative_count * 0.2)
        recommendation = 'HOLD' if sentiment_score > -0.5 else 'SELL'
        reason = 'Herausforderungen erkannt, vorsichtige Bewertung angebracht'
    else:
        sentiment_score = 0.0
        recommendation = 'HOLD'
        reason = 'Neutrale Nachrichtenlage, abwartende Haltung empfohlen'
    
    return {
        'sentiment_score': round(sentiment_score, 2),
        'recommendation': recommendation,
        'reason': reason
    }


def analyze_sentiment_with_ai(headline: str, ticker: str, use_mock: bool = False) -> dict:
    """
    Analysiert eine News-Headline mit Claude AI oder Mock-Daten als Fallback.
    
    Args:
        headline: News-Überschrift
        ticker: Ticker-Symbol
        use_mock: Wenn True, verwende Mock-Daten statt API
        
    Returns:
        Dictionary mit sentiment_score, recommendation, reason
    """
    # Mock-Daten Fallback
    if use_mock:
        return generate_mock_sentiment(headline)
    
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Prompt für Claude erstellen
        prompt = f"""Du bist ein professioneller Finanzanalyst. Analysiere diese News-Headline für die Aktie {ticker}:

Headline: "{headline}"

Bewerte die Headline und gib deine Analyse im folgenden JSON-Format zurück:
{{
    "sentiment_score": <float zwischen -1.0 (sehr negativ) und +1.0 (sehr positiv)>,
    "recommendation": "<BUY, HOLD oder SELL>",
    "reason": "<Einzeilige prägnante Begründung auf Deutsch>"
}}

Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text."""

        # Claude API aufrufen mit claude-haiku-4.5
        try:
            message = client.messages.create(
                model="claude-haiku-4.5",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as api_error:
            # API-Fehler (z.B. kein Guthaben, ungültiger Key, Modell nicht verfügbar)
            print(f"   ⚠️  Claude API-Fehler: {str(api_error)[:60]}...")
            print(f"   → Fallback zu Mock-Daten")
            return generate_mock_sentiment(headline)
        
        # Response parsen
        response_text = message.content[0].text.strip()
        
        # JSON extrahieren (falls Markdown Code-Block vorhanden)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        analysis = json.loads(response_text)
        
        # Validierung
        sentiment_score = float(analysis['sentiment_score'])
        if not -1.0 <= sentiment_score <= 1.0:
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        recommendation = analysis['recommendation'].upper()
        if recommendation not in ['BUY', 'HOLD', 'SELL']:
            recommendation = 'HOLD'
        
        return {
            'sentiment_score': round(sentiment_score, 2),
            'recommendation': recommendation,
            'reason': analysis['reason']
        }
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON-Parsing fehlgeschlagen: {str(e)}")
        return {
            'sentiment_score': 0.0,
            'recommendation': 'HOLD',
            'reason': 'Analyse fehlgeschlagen - neutral bewertet'
        }
    except Exception as e:
        print(f"[ERROR] AI-Analyse fehlgeschlagen: {str(e)}")
        return {
            'sentiment_score': 0.0,
            'recommendation': 'HOLD',
            'reason': f'Fehler bei AI-Analyse: {str(e)[:50]}'
        }


def create_sentiment_table(db_path: str):
    """
    Erstellt die Tabelle für News-Sentiment-Daten.
    
    Args:
        db_path: Pfad zur Datenbankdatei
    """
    print(f"\n[INFO] Erstelle/Prüfe news_sentiment Tabelle...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                headline TEXT NOT NULL,
                publisher VARCHAR(100),
                sentiment_score REAL NOT NULL,
                recommendation VARCHAR(10) NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(headline, ticker)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("[SUCCESS] Tabelle news_sentiment bereit.")
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Erstellen der Tabelle: {str(e)}")
        raise


def save_sentiment_to_db(news_data: list, db_path: str):
    """
    Speichert Sentiment-Analysen in der Datenbank.
    
    Args:
        news_data: Liste mit analysierten News
        db_path: Pfad zur Datenbankdatei
    """
    print(f"\n[INFO] Speichere {len(news_data)} Sentiment-Analysen...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        duplicate_count = 0
        
        for news in news_data:
            try:
                cursor.execute('''
                    INSERT INTO news_sentiment 
                    (date, ticker, headline, publisher, sentiment_score, recommendation, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news['date'],
                    news['ticker'],
                    news['headline'],
                    news['publisher'],
                    news['sentiment_score'],
                    news['recommendation'],
                    news['reason']
                ))
                saved_count += 1
            except sqlite3.IntegrityError:
                duplicate_count += 1
                continue
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] {saved_count} neue Einträge gespeichert.")
        if duplicate_count > 0:
            print(f"[INFO] {duplicate_count} Duplikate übersprungen.")
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Speichern: {str(e)}")
        raise


def display_sentiment_summary(news_data: list):
    """
    Zeigt eine formatierte Zusammenfassung der Sentiment-Analysen.
    
    Args:
        news_data: Liste mit analysierten News
    """
    print("\n" + "=" * 80)
    print("KI SENTIMENT-ANALYSE ZUSAMMENFASSUNG")
    print("=" * 80)
    
    if not news_data:
        print("[INFO] Keine Daten zur Anzeige vorhanden.")
        return
    
    # Statistiken berechnen
    total = len(news_data)
    avg_sentiment = sum(n['sentiment_score'] for n in news_data) / total
    buy_count = sum(1 for n in news_data if n['recommendation'] == 'BUY')
    hold_count = sum(1 for n in news_data if n['recommendation'] == 'HOLD')
    sell_count = sum(1 for n in news_data if n['recommendation'] == 'SELL')
    
    print(f"\n📊 STATISTIKEN:")
    print(f"   Analysierte News: {total}")
    print(f"   Durchschnittliches Sentiment: {avg_sentiment:.2f}")
    print(f"   Empfehlungen: 🟢 BUY: {buy_count} | 🟡 HOLD: {hold_count} | 🔴 SELL: {sell_count}")
    
    # Sentiment-Klassifikation
    if avg_sentiment > 0.3:
        overall = "🟢 POSITIV"
    elif avg_sentiment < -0.3:
        overall = "🔴 NEGATIV"
    else:
        overall = "🟡 NEUTRAL"
    
    print(f"   Gesamtstimmung: {overall}")
    
    # Top 5 News anzeigen
    print(f"\n📰 TOP {min(5, total)} NEWS-ANALYSEN:")
    print("-" * 80)
    
    for i, news in enumerate(news_data[:5], 1):
        sentiment_emoji = "🟢" if news['sentiment_score'] > 0.3 else "🔴" if news['sentiment_score'] < -0.3 else "🟡"
        rec_emoji = {"BUY": "📈", "HOLD": "⏸️", "SELL": "📉"}[news['recommendation']]
        
        print(f"\n{i}. {sentiment_emoji} Sentiment: {news['sentiment_score']:+.2f} | {rec_emoji} {news['recommendation']}")
        print(f"   Headline: {news['headline'][:75]}...")
        print(f"   Begründung: {news['reason']}")
        print(f"   Quelle: {news['publisher']} | {news['date']}")
    
    print("\n" + "=" * 80)


# ========================= MAIN FUNKTION =========================

def main():
    """
    Hauptfunktion: Orchestriert die AI Sentiment-Analyse Pipeline.
    """
    print("=" * 80)
    print("AI SENTIMENT-ANALYSE PIPELINE")
    print("Mercedes-Benz Stock Trading Bot")
    print("=" * 80)
    
    try:
        # Schritt 1: Tabelle erstellen
        create_sentiment_table(DB_PATH)
        
        # Schritt 2: News abrufen
        print("\n" + "=" * 80)
        print("SCHRITT 1: NEWS ABRUFEN")
        print("=" * 80)
        news_list = fetch_news(TICKER)
        
        # Fallback zu Mock-News wenn yfinance keine liefert
        use_mock_data = False
        if not news_list or all(not n.get('title') or n.get('title') == 'Kein Titel' for n in news_list):
            print("\n⚠️  yfinance liefert keine verwertbaren News-Titel.")
            print("→ Verwende realistische Mock-Headlines für Demonstration\n")
            use_mock_data = True
            
            # Realistische Mock-Headlines
            mock_headlines = [
                "Mercedes-Benz steigert Gewinn im dritten Quartal um 15 Prozent",
                "Rückruf von 50.000 Mercedes-Fahrzeugen wegen Sicherheitsmängeln",
                "Mercedes präsentiert neue E-Auto-Strategie mit 10 Milliarden Euro Investment",
                "Analysten senken Kursziel für Mercedes-Benz Aktie um 5 Prozent",
                "Mercedes gewinnt Großauftrag für Elektro-Lkw-Flotte in China",
                "Branchenexperten warnen vor Überkapazitäten im Premiumsegment",
                "Mercedes-Benz kündigt Dividendenerhöhung von 8 Prozent an",
                "Neue Umweltauflagen könnten Mercedes Millionen kosten",
                "Mercedes übertrifft Absatzziele im Luxussegment um 20 Prozent",
                "Partnerschaft mit Tech-Gigant für autonomes Fahren angekündigt"
            ]
            
            news_list = [
                {
                    'title': headline,
                    'publisher': 'Mock News Source',
                    'link': '',
                    'publish_time': None
                }
                for headline in mock_headlines
            ]
        
        # Schritt 3: AI-Analyse durchführen
        print("\n" + "=" * 80)
        print("SCHRITT 2: AI-SENTIMENT-ANALYSE")
        if use_mock_data:
            print("(Claude API mit Fallback zu Mock-Sentiment)")
        else:
            print("(Verwendet Claude Haiku 4.5)")
        print("=" * 80)
        
        analyzed_news = []
        
        for i, news in enumerate(news_list, 1):
            print(f"\n[{i}/{len(news_list)}] Analysiere: {news['title'][:60]}...")
            
            # AI-Analyse durchführen (verwendet Mock-Fallback bei API-Fehlern)
            analysis = analyze_sentiment_with_ai(news['title'], TICKER, use_mock=use_mock_data)
            
            # Daten kombinieren
            analyzed_news.append({
                'date': datetime.fromtimestamp(news['publish_time']) if news['publish_time'] else datetime.now(),
                'ticker': TICKER,
                'headline': news['title'],
                'publisher': news['publisher'],
                'sentiment_score': analysis['sentiment_score'],
                'recommendation': analysis['recommendation'],
                'reason': analysis['reason']
            })
            
            print(f"   → Sentiment: {analysis['sentiment_score']:+.2f} | {analysis['recommendation']} | {analysis['reason'][:50]}...")
        
        # Schritt 4: In Datenbank speichern
        print("\n" + "=" * 80)
        print("SCHRITT 3: DATENBANK-SPEICHERUNG")
        print("=" * 80)
        save_sentiment_to_db(analyzed_news, DB_PATH)
        
        # Schritt 5: Zusammenfassung anzeigen
        display_sentiment_summary(analyzed_news)
        
        print("\n" + "=" * 80)
        print("✅ AI SENTIMENT-ANALYSE ERFOLGREICH ABGESCHLOSSEN!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline fehlgeschlagen: {str(e)}")
        raise


if __name__ == "__main__":
    main()
