"""Test der AI-Sentiment Funktion"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

print("Testing Anthropic API...")
print(f"API Key gefunden: {bool(api_key)}\n")

try:
    client = Anthropic(api_key=api_key)
    
    headline = "Mercedes-Benz steigert Gewinn um 15% im dritten Quartal"
    
    prompt = f"""Du bist ein professioneller Finanzanalyst. Analysiere diese News-Headline:

Headline: "{headline}"

Bewerte die Headline und gib deine Analyse im folgenden JSON-Format zurück:
{{
    "sentiment_score": <float zwischen -1.0 und +1.0>,
    "recommendation": "<BUY, HOLD oder SELL>",
    "reason": "<Einzeilige Begründung>"
}}

Antworte NUR mit dem JSON-Objekt."""

    print("Sende Request an Claude API...")
    
    # Try different models
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet-20240620",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    message = None
    for model in models_to_try:
        try:
            print(f"Versuche Modell: {model}")
            message = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            print(f"✅ Erfolgreich mit Modell: {model}\n")
            break
        except Exception as e:
            print(f"   ❌ {model} nicht verfügbar")
            continue
    
    if not message:
        raise Exception("Kein Modell verfügbar")
    
    response_text = message.content[0].text.strip()
    print(f"\nClaude Antwort:\n{response_text}\n")
    
    # JSON parsen
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0].strip()
    
    analysis = json.loads(response_text)
    
    print("✅ Erfolgreiche Analyse:")
    print(f"   Sentiment: {analysis['sentiment_score']}")
    print(f"   Empfehlung: {analysis['recommendation']}")
    print(f"   Begründung: {analysis['reason']}")
    
except Exception as e:
    print(f"❌ Fehler: {type(e).__name__}: {str(e)}")
