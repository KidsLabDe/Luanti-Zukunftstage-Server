#!/bin/bash
# Startet eine Zukunftstage-Welt mit Grief-Analyzer
#
# Verwendung:
#   ./startWorld.sh <weltordner> [port] [analyzer-port]
#
# Beispiele:
#   ./startWorld.sh 02-koeln              # Port 30000, Analyzer 8080
#   ./startWorld.sh 02-koeln 30102        # Port 30102, Analyzer 8080
#   ./startWorld.sh 01 30101 9000         # Port 30101, Analyzer 9000
#
# Server: Server-IP:<port>
# Analyzer: http://localhost:<analyzer-port>

set -e

WORLD_FOLDER="${1}"
PORT="${2:-30000}"
ANALYZER_PORT="${3:-8080}"

if [ -z "$WORLD_FOLDER" ]; then
    echo "Verfügbare Welten:"
    ls -1 worlds/
    echo ""
    read -p "Weltordner eingeben: " WORLD_FOLDER
fi

WORLD_PATH="./worlds/${WORLD_FOLDER}"

# Prüfen ob Welt existiert
if [ ! -d "$WORLD_PATH" ]; then
    echo "Fehler: Welt '$WORLD_FOLDER' nicht gefunden in $WORLD_PATH"
    exit 1
fi

# world_name aus world.mt extrahieren
WORLD_MT="${WORLD_PATH}/world.mt"
if [ -f "$WORLD_MT" ]; then
    WORLDNAME=$(grep "^world_name" "$WORLD_MT" | cut -d'=' -f2 | tr -d ' ')
    if [ -z "$WORLDNAME" ]; then
        WORLDNAME="$WORLD_FOLDER"
    fi
else
    echo "Warnung: Keine world.mt gefunden, verwende Ordnername als worldname"
    WORLDNAME="$WORLD_FOLDER"
fi

# Prüfen ob map.dat existiert
if [ ! -f "$WORLD_PATH/world2minetest/map.dat" ]; then
    echo "Warnung: Keine map.dat gefunden in $WORLD_PATH/world2minetest/"
    echo "Die Welt wird ohne OSM-Daten gestartet."
fi

# Logs-Verzeichnis erstellen
mkdir -p "$(pwd)/logs"

echo "======================================"
echo "Starte Zukunftstage-Welt"
echo "======================================"
echo ""
echo "  Welt:      $WORLD_FOLDER"
echo "  Worldname: $WORLDNAME"
echo "  Port:      $PORT"
echo "  Analyzer:  http://localhost:$ANALYZER_PORT"
echo ""

# Umgebungsvariablen setzen und docker compose starten
export WORLD_FOLDER
export WORLDNAME
export PORT
export ANALYZER_PORT

# Alte Container für diese Welt stoppen falls vorhanden
docker compose -p "zfn_${WORLD_FOLDER}" down 2>/dev/null || true

# Starten
docker compose -p "zfn_${WORLD_FOLDER}" up -d --build

echo ""
echo "======================================"
echo "Gestartet!"
echo "======================================"
echo ""
echo "Minetest:  Server-IP:$PORT"
echo "Analyzer:  http://localhost:$ANALYZER_PORT"
echo ""
echo "Befehle:"
echo "  Logs:     docker compose -p zfn_${WORLD_FOLDER} logs -f"
echo "  Stoppen:  docker compose -p zfn_${WORLD_FOLDER} down"
echo "  Status:   docker compose -p zfn_${WORLD_FOLDER} ps"
