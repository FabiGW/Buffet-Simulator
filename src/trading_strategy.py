"""
Trading Strategie für Mercedes-Benz AI Stock Trading Bot
=========================================================
Kombiniert technische Indikatoren (SMA20) mit KI-Sentiment-Analyse
für finale Handelssignale.

Autor: Senior Quant & Software Engineer
Datum: 26.09.2026
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

# Konfiguration
DB_PATH = 'data/stock_data.db'
TICKER = 'MBG.DE'
SMA_PERIOD = 20  # 20-Tage Simple Moving Average

# Trading-Schwellwerte
SENTIMENT_BUY_THRESHOLD = 0.2
SENTIMENT_SELL_THRESHOLD = -0.2


class TradingStrategy:
    """
    Mercedes-Benz Trading Strategie Klasse
    Kombiniert technische Analyse mit AI-Sentiment
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.prices_df = None
        self.sentiment_df = None
        
    def connect_db(self):
        """Verbindung zur Datenbank herstellen"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Datenbankverbindung hergestellt: {self.db_path}")
        
    def load_price_data(self) -> pd.DataFrame:
        """Lädt historische Preisdaten aus der Datenbank"""
        query = """
            SELECT date, open, high, low, close, volume
            FROM mercedes_prices
            ORDER BY date ASC
        """
        self.prices_df = pd.read_sql_query(query, self.conn)
        self.prices_df['date'] = pd.to_datetime(self.prices_df['date'], utc=True).dt.tz_localize(None)
        print(f"✅ {len(self.prices_df)} Preisdatensätze geladen")
        return self.prices_df
    
    def load_sentiment_data(self) -> pd.DataFrame:
        """Lädt AI Sentiment-Daten aus der Datenbank"""
        query = """
            SELECT date, sentiment_score, recommendation, reason
            FROM news_sentiment
            WHERE ticker = ?
            ORDER BY date DESC
        """
        self.sentiment_df = pd.read_sql_query(query, self.conn, params=(TICKER,))
        self.sentiment_df['date'] = pd.to_datetime(self.sentiment_df['date'], utc=True).dt.tz_localize(None)
        print(f"✅ {len(self.sentiment_df)} Sentiment-Datensätze geladen")
        return self.sentiment_df
    
    def calculate_sma(self, period: int = SMA_PERIOD) -> pd.DataFrame:
        """
        Berechnet Simple Moving Average (SMA)
        
        Args:
            period: Anzahl der Tage für SMA-Berechnung
            
        Returns:
            DataFrame mit SMA-Spalte
        """
        self.prices_df[f'SMA{period}'] = self.prices_df['close'].rolling(
            window=period, 
            min_periods=period
        ).mean()
        
        valid_sma = self.prices_df[f'SMA{period}'].notna().sum()
        print(f"✅ SMA{period} berechnet ({valid_sma} gültige Werte)")
        return self.prices_df
    
    def get_latest_sentiment(self, price_date: pd.Timestamp) -> Tuple[float, str]:
        """
        Ermittelt das aktuellste Sentiment vor oder am gegebenen Datum
        
        Args:
            price_date: Datum für das Sentiment-Lookup
            
        Returns:
            Tuple (sentiment_score, reason)
        """
        # Filter Sentiments bis zum gegebenen Datum
        relevant_sentiments = self.sentiment_df[
            self.sentiment_df['date'] <= price_date
        ]
        
        if len(relevant_sentiments) == 0:
            return 0.0, "Kein Sentiment verfügbar"
        
        # Neuestes Sentiment
        latest = relevant_sentiments.iloc[0]
        return latest['sentiment_score'], latest['reason']
    
    def generate_signal(
        self, 
        current_price: float, 
        sma20: float, 
        sentiment_score: float
    ) -> Tuple[str, str]:
        """
        Generiert Handelssignal basierend auf Preis, SMA und Sentiment
        
        Trading-Logik:
        - BUY:  Preis > SMA20 UND Sentiment > 0.2
        - SELL: Preis < SMA20 ODER Sentiment < -0.2
        - HOLD: Alle anderen Fälle
        
        Args:
            current_price: Aktueller Schlusskurs
            sma20: 20-Tage SMA
            sentiment_score: AI Sentiment Score (-1 bis +1)
            
        Returns:
            Tuple (Signal, Begründung)
        """
        price_above_sma = current_price > sma20
        price_below_sma = current_price < sma20
        sentiment_positive = sentiment_score > SENTIMENT_BUY_THRESHOLD
        sentiment_negative = sentiment_score < SENTIMENT_SELL_THRESHOLD
        
        # BUY Signal
        if price_above_sma and sentiment_positive:
            reason = (
                f"Preis (€{current_price:.2f}) über SMA20 (€{sma20:.2f}) "
                f"+ Positives Sentiment ({sentiment_score:+.2f})"
            )
            return "BUY", reason
        
        # SELL Signal
        elif price_below_sma or sentiment_negative:
            if price_below_sma and sentiment_negative:
                reason = (
                    f"Preis (€{current_price:.2f}) unter SMA20 (€{sma20:.2f}) "
                    f"+ Negatives Sentiment ({sentiment_score:+.2f})"
                )
            elif price_below_sma:
                reason = (
                    f"Preis (€{current_price:.2f}) unter SMA20 (€{sma20:.2f})"
                )
            else:
                reason = (
                    f"Negatives Sentiment ({sentiment_score:+.2f}) "
                    f"unter Schwellwert ({SENTIMENT_SELL_THRESHOLD})"
                )
            return "SELL", reason
        
        # HOLD Signal
        else:
            reason = (
                f"Neutral: Preis (€{current_price:.2f}) vs SMA20 (€{sma20:.2f}), "
                f"Sentiment ({sentiment_score:+.2f})"
            )
            return "HOLD", reason
    
    def create_trading_signals_table(self):
        """Erstellt die Tabelle für Trading-Signale"""
        cursor = self.conn.cursor()
        
        # Tabelle löschen falls vorhanden
        cursor.execute("DROP TABLE IF EXISTS trading_signals")
        
        # Neue Tabelle erstellen
        cursor.execute("""
            CREATE TABLE trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datum TIMESTAMP NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                aktueller_preis REAL NOT NULL,
                sma20 REAL NOT NULL,
                sentiment_score REAL NOT NULL,
                signal VARCHAR(10) NOT NULL,
                begruendung TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        print("✅ Tabelle 'trading_signals' erstellt")
    
    def save_signals(self, signals: List[Dict]):
        """
        Speichert generierte Signale in der Datenbank
        
        Args:
            signals: Liste von Signal-Dictionaries
        """
        cursor = self.conn.cursor()
        
        for signal in signals:
            # Konvertiere Timestamp zu String für SQLite
            datum_str = signal['datum'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(signal['datum'], 'strftime') else str(signal['datum'])
            
            cursor.execute("""
                INSERT INTO trading_signals 
                (datum, ticker, aktueller_preis, sma20, sentiment_score, signal, begruendung)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datum_str,
                signal['ticker'],
                signal['aktueller_preis'],
                signal['sma20'],
                signal['sentiment_score'],
                signal['signal'],
                signal['begruendung']
            ))
        
        self.conn.commit()
        print(f"✅ {len(signals)} Handelssignale gespeichert")
    
    def run(self):
        """Hauptausführung der Trading-Strategie"""
        print("=" * 80)
        print("🤖 MERCEDES-BENZ AI TRADING STRATEGY")
        print("=" * 80)
        print(f"Ticker: {TICKER}")
        print(f"SMA-Periode: {SMA_PERIOD} Tage")
        print(f"Sentiment Buy-Schwellwert: >{SENTIMENT_BUY_THRESHOLD}")
        print(f"Sentiment Sell-Schwellwert: <{SENTIMENT_SELL_THRESHOLD}")
        print("=" * 80 + "\n")
        
        # 1. Datenbank verbinden
        self.connect_db()
        
        # 2. Daten laden
        print("\n📊 LADE DATEN...")
        self.load_price_data()
        self.load_sentiment_data()
        
        # 3. SMA berechnen
        print("\n📈 BERECHNE TECHNISCHE INDIKATOREN...")
        self.calculate_sma(SMA_PERIOD)
        
        # 4. Signale generieren
        print("\n🎯 GENERIERE HANDELSSIGNALE...")
        signals = []
        
        # Nur Tage mit gültigem SMA
        valid_data = self.prices_df[self.prices_df[f'SMA{SMA_PERIOD}'].notna()].copy()
        
        for idx, row in valid_data.iterrows():
            date = row['date']
            current_price = row['close']
            sma20 = row[f'SMA{SMA_PERIOD}']
            
            # Sentiment für diesen Tag
            sentiment_score, sentiment_reason = self.get_latest_sentiment(date)
            
            # Signal generieren
            signal, reason = self.generate_signal(current_price, sma20, sentiment_score)
            
            signals.append({
                'datum': date,
                'ticker': TICKER,
                'aktueller_preis': current_price,
                'sma20': sma20,
                'sentiment_score': sentiment_score,
                'signal': signal,
                'begruendung': reason
            })
        
        print(f"   {len(signals)} Signale generiert")
        
        # 5. Tabelle erstellen und Signale speichern
        print("\n💾 SPEICHERE SIGNALE...")
        self.create_trading_signals_table()
        self.save_signals(signals)
        
        # 6. Aktuellstes Signal anzeigen
        self.display_latest_signal(signals)
        
        # 7. Statistik
        self.display_statistics(signals)
        
        # Verbindung schließen
        self.conn.close()
        print("\n" + "=" * 80)
        print("✅ TRADING-STRATEGIE ERFOLGREICH AUSGEFÜHRT")
        print("=" * 80 + "\n")
    
    def display_latest_signal(self, signals: List[Dict]):
        """Zeigt das aktuellste Handelssignal formatiert an"""
        if not signals:
            print("⚠️  Keine Signale verfügbar")
            return
        
        latest = signals[-1]  # Letztes Signal (neuestes Datum)
        
        print("\n" + "=" * 80)
        print("🎯 AKTUELLSTES HANDELSSIGNAL")
        print("=" * 80)
        
        # Signal-Emoji
        signal_emoji = {
            "BUY": "🟢 📈",
            "SELL": "🔴 📉",
            "HOLD": "🟡 ⏸️"
        }
        
        print(f"\n{signal_emoji.get(latest['signal'], '⚪')} SIGNAL: {latest['signal']}")
        print(f"\n📅 Datum:              {latest['datum'].strftime('%Y-%m-%d')}")
        print(f"🏷️  Ticker:             {latest['ticker']}")
        print(f"💰 Aktueller Preis:    €{latest['aktueller_preis']:.2f}")
        print(f"📊 SMA20:              €{latest['sma20']:.2f}")
        print(f"🤖 KI-Sentiment:       {latest['sentiment_score']:+.2f}")
        print(f"\n💡 BEGRÜNDUNG:")
        print(f"   {latest['begruendung']}")
        print("\n" + "=" * 80)
    
    def display_statistics(self, signals: List[Dict]):
        """Zeigt Statistik über alle generierten Signale"""
        if not signals:
            return
        
        buy_count = sum(1 for s in signals if s['signal'] == 'BUY')
        hold_count = sum(1 for s in signals if s['signal'] == 'HOLD')
        sell_count = sum(1 for s in signals if s['signal'] == 'SELL')
        
        total = len(signals)
        
        print("\n📊 SIGNAL-STATISTIK:")
        print(f"   Gesamt:     {total} Signale")
        print(f"   🟢 BUY:     {buy_count} ({buy_count/total*100:.1f}%)")
        print(f"   🟡 HOLD:    {hold_count} ({hold_count/total*100:.1f}%)")
        print(f"   🔴 SELL:    {sell_count} ({sell_count/total*100:.1f}%)")
        
        # Durchschnittswerte
        avg_price = sum(s['aktueller_preis'] for s in signals) / total
        avg_sentiment = sum(s['sentiment_score'] for s in signals) / total
        
        print(f"\n📈 DURCHSCHNITTSWERTE:")
        print(f"   Ø Preis:        €{avg_price:.2f}")
        print(f"   Ø Sentiment:    {avg_sentiment:+.2f}")


def main():
    """Hauptfunktion"""
    strategy = TradingStrategy()
    strategy.run()


if __name__ == "__main__":
    main()

