#!/bin/bash

# generate_world.sh - Erzeugt eine Minetest-Welt aus OpenStreetMap-Daten
#
# Verwendung:
#   ./generate_world.sh                              # Interaktiver Modus
#   ./generate_world.sh -p "02-Muenchen" -a "48.12,11.54,48.14,11.58"
#   ./generate_world.sh --name "02-Muenchen" --area "48.12,11.54,48.14,11.58"
#
# Optionen:
#   -p, --name      Projektname (z.B. "02-Muenchen")
#   -a, --area      Koordinaten: lat1,lon1,lat2,lon2 (z.B. "48.12,11.54,48.14,11.58")
#   -g, --game      Game-ID (Standard: mineclonia)
#   -b, --backend   Datenbank-Backend (Standard: leveldb)
#   -m, --minimap   Minimap generieren
#   -r, --reuse     Query wiederverwenden
#   -h, --help      Diese Hilfe anzeigen

set -e

# Standardwerte
GAME="mineclonia"
BACKEND="leveldb"
MINIMAP=""
REUSE=""
NAME=""
AREA=""

# Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hilfe anzeigen
show_help() {
    echo "Verwendung: $0 [OPTIONEN]"
    echo ""
    echo "Erzeugt eine Minetest-Welt aus OpenStreetMap-Daten."
    echo ""
    echo "Optionen:"
    echo "  -p, --name NAME       Projektname (z.B. '02-Muenchen')"
    echo "  -a, --area COORDS     Koordinaten: lat1,lon1,lat2,lon2"
    echo "                        Beispiel: '48.12,11.54,48.14,11.58'"
    echo "  -g, --game GAME       Game-ID (Standard: mineclonia)"
    echo "  -b, --backend DB      Datenbank-Backend: sqlite3|leveldb (Standard: leveldb)"
    echo "  -m, --minimap         Minimap.png generieren"
    echo "  -r, --reuse           Vorhandene Query wiederverwenden"
    echo "  -h, --help            Diese Hilfe anzeigen"
    echo ""
    echo "Beispiele:"
    echo "  $0 -p '02-Muenchen' -a '48.12,11.54,48.14,11.58'"
    echo "  $0 --name '03-Berlin' --area '52.51,13.38,52.52,13.40' --minimap"
    echo "  $0  # Interaktiver Modus"
    echo ""
    echo "Koordinaten-Tipp:"
    echo "  Öffne Google Maps, rechtsklicke auf zwei gegenüberliegende Ecken"
    echo "  des gewünschten Bereichs und kopiere die Koordinaten."
    echo "  Format: Breitengrad,Längengrad (z.B. 48.137154,11.576124)"
}

# Kommandozeilen-Argumente parsen
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--name)
            NAME="$2"
            shift 2
            ;;
        -a|--area)
            AREA="$2"
            shift 2
            ;;
        -g|--game)
            GAME="$2"
            shift 2
            ;;
        -b|--backend)
            BACKEND="$2"
            shift 2
            ;;
        -m|--minimap)
            MINIMAP="-m"
            shift
            ;;
        -r|--reuse)
            REUSE="-r"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Ins Skript-Verzeichnis wechseln
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# MINETEST_GAME_PATH setzen (Hauptverzeichnis)
export MINETEST_GAME_PATH="$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Luanti/Minetest Welt-Generator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Interaktive Eingabe falls Parameter fehlen
if [ -z "$NAME" ]; then
    echo -e "${YELLOW}Projektname eingeben${NC}"
    echo "  Format: XX-Stadtname (z.B. 02-Muenchen)"
    echo -n "> "
    read NAME
    if [ -z "$NAME" ]; then
        echo -e "${RED}Fehler: Projektname ist erforderlich${NC}"
        exit 1
    fi
fi

if [ -z "$AREA" ] && [ -z "$REUSE" ]; then
    echo ""
    echo -e "${YELLOW}Koordinaten eingeben${NC}"
    echo "  Format: lat1,lon1,lat2,lon2"
    echo "  Beispiel: 48.12,11.54,48.14,11.58"
    echo "  (Zwei gegenüberliegende Ecken des Bereichs)"
    echo -n "> "
    read AREA
    if [ -z "$AREA" ]; then
        echo -e "${RED}Fehler: Koordinaten sind erforderlich${NC}"
        exit 1
    fi
fi

# Optionale Parameter abfragen wenn interaktiv
if [ -z "$MINIMAP" ]; then
    echo ""
    echo -e "${YELLOW}Minimap generieren? [j/N]${NC}"
    echo -n "> "
    read MINIMAP_CHOICE
    if [[ "$MINIMAP_CHOICE" =~ ^[jJyY]$ ]]; then
        MINIMAP="-m"
    fi
fi

# Kommandozeile zusammenbauen
CMD="python3 w2mt/w2mt.py -p \"$NAME\" -g \"$GAME\" -b \"$BACKEND\""

if [ -n "$AREA" ]; then
    CMD="$CMD -a \"$AREA\""
fi

if [ -n "$MINIMAP" ]; then
    CMD="$CMD $MINIMAP"
fi

if [ -n "$REUSE" ]; then
    CMD="$CMD $REUSE"
fi

# Zusammenfassung und Kommando anzeigen
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Konfiguration:${NC}"
echo -e "  Projektname:  ${YELLOW}$NAME${NC}"
if [ -n "$AREA" ]; then
    echo -e "  Koordinaten:  ${YELLOW}$AREA${NC}"
fi
echo -e "  Game:         ${YELLOW}$GAME${NC}"
echo -e "  Backend:      ${YELLOW}$BACKEND${NC}"
if [ -n "$MINIMAP" ]; then
    echo -e "  Minimap:      ${YELLOW}Ja${NC}"
fi
if [ -n "$REUSE" ]; then
    echo -e "  Query reuse:  ${YELLOW}Ja${NC}"
fi
echo ""
echo -e "${GREEN}Auszuführender Befehl:${NC}"
echo -e "  ${YELLOW}$CMD${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Bestätigung
echo -e "${YELLOW}Welt generieren? [J/n]${NC}"
echo -n "> "
read CONFIRM
if [[ "$CONFIRM" =~ ^[nN]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

echo ""
echo -e "${GREEN}Starte Welt-Generierung...${NC}"
echo ""

# In w2mt-Verzeichnis wechseln und ausführen
cd "$SCRIPT_DIR/w2mt"
export MINETEST_GAME_PATH="$SCRIPT_DIR"

# Python venv prüfen und aktivieren
VENV_OK=false
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    # Prüfe ob venv funktioniert (pip verfügbar)
    if python3 -c "import pip" 2>/dev/null; then
        # Prüfe ob Abhängigkeiten installiert sind
        if python3 -c "import pyproj" 2>/dev/null; then
            echo -e "${BLUE}Python venv aktiviert${NC}"
            VENV_OK=true
        else
            echo -e "${YELLOW}Installiere fehlende Abhängigkeiten...${NC}"
            pip install -r requirements.txt && VENV_OK=true
        fi
    fi
fi

if [ "$VENV_OK" = false ]; then
    echo -e "${YELLOW}venv defekt oder fehlt. Erstelle neu...${NC}"
    deactivate 2>/dev/null
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${BLUE}Installiere Abhängigkeiten...${NC}"
    pip install -r requirements.txt
fi

# Ausführen
eval "python3 w2mt.py -p \"$NAME\" -g \"$GAME\" -b \"$BACKEND\" ${AREA:+-a \"$AREA\"} $MINIMAP $REUSE"

# venv deaktivieren falls aktiviert
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Welt-Generierung abgeschlossen!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Die Welt wurde erstellt in:"
echo -e "  ${YELLOW}worlds/$NAME/${NC}"
echo ""
echo -e "Zum Starten:"
echo -e "  ${YELLOW}docker compose -f XX.yaml up${NC}"
echo -e "  (wobei XX die Weltnummer ist)"
