# 🤖 Mercedes-Benz AI Trading Strategy

## 📋 Übersicht

Das **Trading Strategy Modul** (`src/trading_strategy.py`) ist das Herzstück des AI Stock Trading Bots für Mercedes-Benz (MBG.DE). Es kombiniert **technische Indikatoren** mit **KI-Sentiment-Analyse**, um fundierte Handelssignale zu generieren.

---

## 🎯 Funktionen

### 1. Datenintegration
- Lädt historische Kursdaten aus `mercedes_prices` Tabelle
- Importiert AI-Sentiment-Analysen aus `news_sentiment` Tabelle
- Automatische Timezone-Normalisierung

### 2. Technische Analyse
- **SMA20** (20-Tage Simple Moving Average) Berechnung
- Trendanalyse basierend auf Preis vs. SMA

### 3. Trading-Logik

#### 🟢 BUY Signal
- Aktueller Preis > SMA20 **UND** KI-Sentiment Score > **+0.2**

#### 🔴 SELL Signal
- Aktueller Preis < SMA20 **ODER** KI-Sentiment Score < **-0.2**

#### 🟡 HOLD Signal
- Alle anderen Fälle (neutrale Marktlage)

### 4. Datenpersistenz
- Speichert alle Signale in `trading_signals` Tabelle
- Vollständige Nachvollziehbarkeit mit Begründungen

---

## 🗄️ Datenbank-Schema: `trading_signals`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | INTEGER | Primary Key (Auto-Increment) |
| datum | TIMESTAMP | Handelsdatum |
| ticker | VARCHAR(20) | Aktiensymbol (MBG.DE) |
| aktueller_preis | REAL | Schlusskurs des Tages |
| sma20 | REAL | 20-Tage Moving Average |
| sentiment_score | REAL | KI-Sentiment (-1.0 bis +1.0) |
| signal | VARCHAR(10) | BUY / SELL / HOLD |
| begruendung | TEXT | Begründung für das Signal |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

---

## 🚀 Verwendung

```bash
python src/trading_strategy.py
```

---

## 📊 Aktuelle Ergebnisse (26.09.2026)

- **487 Handelssignale** generiert
- **Aktuelles Signal:** 🔴 **SELL** 
- **Grund:** Preis €41.28 liegt **9.5%** unter SMA20 (€45.60)
- **Sentiment:** Neutral (0.00)

### Signal-Verteilung
- 🟢 **BUY:** 0 Signale (0.0%)
- 🟡 **HOLD:** 250 Signale (51.3%)
- 🔴 **SELL:** 237 Signale (48.7%)

**Interpretation:** Mercedes-Benz befindet sich in einem **Abwärtstrend**.

---

## 🔧 Konfiguration

```python
DB_PATH = 'data/stock_data.db'
TICKER = 'MBG.DE'
SMA_PERIOD = 20
SENTIMENT_BUY_THRESHOLD = 0.2
SENTIMENT_SELL_THRESHOLD = -0.2
```

---

## 🎓 Interview-Demonstration

✅ Quantitative Analyse  
✅ AI Integration  
✅ Datenbank-Engineering  
✅ Software-Architektur  
✅ Data Science  
✅ Produktionsreifer Code  

---

**🚗 Built for Mercedes-Benz | 🤖 Powered by AI | 📊 Driven by Data**
