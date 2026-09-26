"""
Data Pipeline für AI Stock Trading Bot
Lädt historische Aktienkurse von Mercedes-Benz und DAX und speichert sie in SQLite.

Author: Senior Data Engineer
Purpose: Mercedes-Benz Interview Demonstration
"""

import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os


# ========================= KONFIGURATION =========================
TICKERS = {
    'mercedes': 'MBG.DE',
    'dax': '^GDAXI'
}

DB_PATH = os.path.join('data', 'stock_data.db')
YEARS_OF_DATA = 2


# ========================= FUNKTIONEN =========================

def download_stock_data(ticker: str, period_years: int = 2) -> pd.DataFrame:
    """
    Lädt historische Aktienkurse von Yahoo Finance.
    
    Args:
        ticker: Ticker-Symbol (z.B. 'MBG.DE')
        period_years: Anzahl der Jahre für historische Daten
        
    Returns:
        DataFrame mit historischen Kursdaten
    """
    print(f"[INFO] Lade Daten für {ticker}...")
    
    try:
        # Berechne Startdatum
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_years * 365)
        
        # Daten von Yahoo Finance abrufen
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"[WARNING] Keine Daten für {ticker} gefunden!")
            return None
        
        # Index zurücksetzen (Date als Spalte)
        df.reset_index(inplace=True)
        
        # Spaltennamen bereinigen
        df.columns = [col.replace(' ', '_') for col in df.columns]
        
        print(f"[SUCCESS] {len(df)} Datensätze für {ticker} geladen.")
        print(f"[INFO] Zeitraum: {df['Date'].min()} bis {df['Date'].max()}")
        
        return df
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Laden von {ticker}: {str(e)}")
        return None


def create_database(db_path: str):
    """
    Erstellt die SQLite-Datenbank und die Tabellen.
    
    Args:
        db_path: Pfad zur Datenbankdatei
    """
    print(f"\n[INFO] Erstelle Datenbank unter {db_path}...")
    
    try:
        # Verbindung zur Datenbank herstellen (erstellt DB falls nicht vorhanden)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabelle für Mercedes-Benz erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mercedes_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                dividends REAL,
                stock_splits REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        ''')
        
        # Tabelle für DAX erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dax_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                dividends REAL,
                stock_splits REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("[SUCCESS] Datenbank und Tabellen erfolgreich erstellt.")
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Erstellen der Datenbank: {str(e)}")
        raise


def save_to_database(df: pd.DataFrame, table_name: str, db_path: str):
    """
    Speichert DataFrame in SQLite-Datenbank.
    
    Args:
        df: DataFrame mit Aktienkursen
        table_name: Name der Zieltabelle
        db_path: Pfad zur Datenbankdatei
    """
    print(f"\n[INFO] Speichere Daten in Tabelle '{table_name}'...")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Spaltennamen für Datenbank vorbereiten
        df_to_save = df.copy()
        df_to_save.columns = df_to_save.columns.str.lower()
        
        # Nur relevante Spalten auswählen
        columns_to_save = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
        df_to_save = df_to_save[columns_to_save]
        
        # In Datenbank speichern (replace = überschreibe falls vorhanden)
        df_to_save.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"[SUCCESS] {len(df_to_save)} Datensätze in '{table_name}' gespeichert.")
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Speichern in '{table_name}': {str(e)}")
        raise


def verify_database(db_path: str):
    """
    Überprüft die Datenbank und zeigt Statistiken an.
    
    Args:
        db_path: Pfad zur Datenbankdatei
    """
    print(f"\n[INFO] Verifiziere Datenbank...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Mercedes-Daten prüfen
        cursor.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM mercedes_prices")
        merc_count, merc_min, merc_max = cursor.fetchone()
        print(f"[INFO] Mercedes-Benz: {merc_count} Datensätze ({merc_min} bis {merc_max})")
        
        # DAX-Daten prüfen
        cursor.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM dax_prices")
        dax_count, dax_min, dax_max = cursor.fetchone()
        print(f"[INFO] DAX: {dax_count} Datensätze ({dax_min} bis {dax_max})")
        
        # Beispieldaten anzeigen
        print("\n[INFO] Beispiel Mercedes-Benz Daten (letzte 5 Einträge):")
        cursor.execute("SELECT date, open, high, low, close, volume FROM mercedes_prices ORDER BY date DESC LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row[0]}: Open={row[1]:.2f}, High={row[2]:.2f}, Low={row[3]:.2f}, Close={row[4]:.2f}, Vol={row[5]}")
        
        conn.close()
        
        print("\n[SUCCESS] Datenbankverifizierung abgeschlossen!")
        
    except Exception as e:
        print(f"[ERROR] Fehler bei der Verifizierung: {str(e)}")


# ========================= MAIN FUNKTION =========================

def main():
    """
    Hauptfunktion: Orchestriert den gesamten Data Pipeline Prozess.
    """
    print("=" * 70)
    print("AI STOCK TRADING BOT - DATA PIPELINE")
    print("Mercedes-Benz Interview Demonstration")
    print("=" * 70)
    
    try:
        # Schritt 1: Datenbank erstellen
        create_database(DB_PATH)
        
        # Schritt 2: Mercedes-Benz Daten laden und speichern
        print("\n" + "=" * 70)
        print("SCHRITT 1: MERCEDES-BENZ DATEN")
        print("=" * 70)
        mercedes_df = download_stock_data(TICKERS['mercedes'], YEARS_OF_DATA)
        
        if mercedes_df is not None:
            save_to_database(mercedes_df, 'mercedes_prices', DB_PATH)
        else:
            print("[WARNING] Mercedes-Daten konnten nicht gespeichert werden.")
        
        # Schritt 3: DAX Daten laden und speichern
        print("\n" + "=" * 70)
        print("SCHRITT 2: DAX DATEN")
        print("=" * 70)
        dax_df = download_stock_data(TICKERS['dax'], YEARS_OF_DATA)
        
        if dax_df is not None:
            save_to_database(dax_df, 'dax_prices', DB_PATH)
        else:
            print("[WARNING] DAX-Daten konnten nicht gespeichert werden.")
        
        # Schritt 4: Datenbank verifizieren
        print("\n" + "=" * 70)
        print("SCHRITT 3: VERIFIZIERUNG")
        print("=" * 70)
        verify_database(DB_PATH)
        
        print("\n" + "=" * 70)
        print("[SUCCESS] DATA PIPELINE ERFOLGREICH ABGESCHLOSSEN!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline fehlgeschlagen: {str(e)}")
        raise


if __name__ == "__main__":
    main()
