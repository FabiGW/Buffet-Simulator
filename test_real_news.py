"""Test: Können wir echte News abrufen?"""
import yfinance as yf

print("=" * 80)
print("TEST: ECHTE NEWS FÜR MERCEDES-BENZ")
print("=" * 80)

ticker = 'MBG.DE'
print(f"\nRufe News für {ticker} ab...\n")

try:
    stock = yf.Ticker(ticker)
    news = stock.news
    
    if news:
        print(f"✅ {len(news)} echte News-Artikel gefunden!\n")
        
        print("📰 ERSTE 5 NEWS:\n")
        for i, article in enumerate(news[:5], 1):
            print(f"{i}. {article.get('title', 'Kein Titel')}")
            print(f"   Quelle: {article.get('publisher', 'Unbekannt')}")
            print(f"   Link: {article.get('link', 'N/A')[:60]}...")
            print()
    else:
        print("⚠️  Keine News gefunden - yfinance liefert aktuell keine News für MBG.DE")
        print("   Alternative: Verwenden Sie die Mock-Data Demo\n")
        
except Exception as e:
    print(f"❌ Fehler: {str(e)}")

print("=" * 80)
