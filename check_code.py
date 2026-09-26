"""Verifiziert das Trading Strategy Skript"""
import os

# Datei-Info
file_path = 'src/trading_strategy.py'
size = os.path.getsize(file_path)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
methods = sum(1 for line in lines if 'def ' in line)

print(f"✅ trading_strategy.py erstellt!")
print(f"   Größe: {size} bytes")
print(f"   Zeilen: {len(lines)}")
print(f"   Methoden: {methods}")
