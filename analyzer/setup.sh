#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python -m venv venv
fi

echo "Installiere Abhängigkeiten..."
./venv/bin/pip install -r requirements.txt

echo ""
echo "Fertig! Nutzung:"
echo "  source venv/bin/activate"
echo "  python analyze.py <logfile> <player>"
