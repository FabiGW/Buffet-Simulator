# 🤖 AI Stock Trading Bot - Sentiment-Analyse Pipeline

**Mercedes-Benz Interview Demonstration**

---

## 📋 Projektübersicht

AI Stock Trading Bot mit historischen Aktienkursen + KI-gestützter Sentiment-Analyse.

### ✅ Features
- 📈 **Historische Kursdaten**: Mercedes-Benz & DAX (2 Jahre)
- 🤖 **AI Sentiment**: Claude AI analysiert News
- 💾 **SQLite DB**: 3 Tabellen (prices, sentiment)
- 🔒 **Security**: API-Keys via `.env`

---

## 🗂️ Struktur

```
Buffet-Simulator/
├── data/stock_data.db           # Datenbank
├── src/
│   ├── data_pipeline.py         # Kursdaten-Pipeline
│   └── ai_sentiment_pipeline.py # AI Sentiment-Analyse
├── .env                          # API-Keys
├── requirements.txt              # Dependencies
└── show_results.py               # Übersicht
```

---

## 🚀 Quick Start

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. API-Key in .env eintragen
ANTHROPIC_API_KEY=sk-ant-...

# 3. Kursdaten laden
python src/data_pipeline.py

# 4. AI Sentiment-Analyse (oder Demo)
python demo_with_mock_data.py

# 5. Ergebnisse anzeigen
python show_results.py
```

---

## 📊 Datenbank-Schema

### `news_sentiment` Tabelle
- `headline`: News-Überschrift
- `sentiment_score`: -1.0 (negativ) bis +1.0 (positiv)
- `recommendation`: BUY, HOLD, SELL
- `reason`: AI-Begründung
- `publisher`, `date`, `ticker`

---

## 🎯 Beispiel-Ausgabe

```
📊 STATISTIKEN:
   Analysierte News: 10
   Durchschnittliches Sentiment: 0.29
   Empfehlungen: 🟢 BUY: 6 | 🟡 HOLD: 4 | 🔴 SELL: 0
   Gesamtstimmung: 🟡 NEUTRAL

📈 TOP NEWS:
1. +0.90 - Partnerschaft mit Tech-Gigant für autonomes Fahren
   → Strategische Allianz beschleunigt Innovation

💡 TRADING-EMPFEHLUNG: 🟢 BUY - Leicht positive Tendenz
```

---

## 🛠️ Tech-Stack

- **Data**: yfinance, pandas
- **AI**: Anthropic Claude
- **DB**: SQLite
- **Security**: python-dotenv
- **Language**: Python 3.13

---

## 🔐 Security

✅ API-Keys in `.env` (nicht im Code)  
✅ `.env` in `.gitignore`  
✅ `.env.example` als Template  
✅ API-Key-Validierung beim Start

---

## 📈 Nächste Schritte

- [ ] Technische Indikatoren (RSI, MACD)
- [ ] LSTM Kursprognosen
- [ ] REST API (FastAPI)
- [ ] Web-Dashboard (Streamlit)
- [ ] Docker Container

---

## 🎓 Interview-Ready

Demonstriert:
- Full-Stack Data Engineering
- AI/ML Integration
- Database Design
- Security Best Practices
- Clean Code & Documentation

---

**🚗 Made for Mercedes-Benz Interview | September 2026**
