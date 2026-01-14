#!/bin/bash
# Startet eine Zukunftstage-Welt mit dem Custom Docker Image
#
# Verwendung:
#   ./startWorld.sh <weltordner> <port>
#
# Beispiele:
#   ./startWorld.sh 02-koeln 30102
#   ./startWorld.sh 01 30101

set -e

# Docker Image - von GitHub Container Registry
IMAGE="ghcr.io/kidslabde/luanti-zukunftstage-server:latest"

WORLD_FOLDER="${1}"
PORT="${2:-30000}"

if [ -z "$WORLD_FOLDER" ]; then
    echo "Verfügbare Welten:"
    ls -1 worlds/
    echo ""
    read -p "Weltordner eingeben: " WORLD_FOLDER
fi

if [ -z "$PORT" ]; then
    read -p "Port eingeben (default: 30000): " PORT
    PORT="${PORT:-30000}"
fi

WORLD_PATH="./worlds/${WORLD_FOLDER}"

# Prüfen ob Welt existiert
if [ ! -d "$WORLD_PATH" ]; then
    echo "Fehler: Welt '$WORLD_FOLDER' nicht gefunden in $WORLD_PATH"
    exit 1
fi

# world_name aus world.mt extrahieren (für --worldname Parameter)
WORLD_MT="${WORLD_PATH}/world.mt"
if [ -f "$WORLD_MT" ]; then
    WORLDNAME=$(grep "^world_name" "$WORLD_MT" | cut -d'=' -f2 | tr -d ' ')
    if [ -z "$WORLDNAME" ]; then
        # Fallback: Ordnername verwenden
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

# Container-Name aus Weltname ableiten (nur alphanumerisch)
CONTAINER_NAME="zfn_$(echo $WORLD_FOLDER | tr -cd '[:alnum:]_-')"

# Logs-Verzeichnis erstellen falls nicht vorhanden
mkdir -p "$(pwd)/logs"

echo "Starte Welt:"
echo "  Ordner:    $WORLD_FOLDER"
echo "  Worldname: $WORLDNAME"
echo "  Port:      $PORT"
echo "  Container: $CONTAINER_NAME"
echo ""

# Docker run mit dem custom image
# Mount unter dem worldname, damit Minetest es findet
docker run -d \
    --name "$CONTAINER_NAME" \
    -e PUID=1000 \
    -e PGID=1000 \
    -e TZ=Europe/Berlin \
    -e "CLI_ARGS=--worldname $WORLDNAME --port $PORT --logfile /config/.minetest/logs/${WORLDNAME}.log" \
    -v "$(pwd)/worlds/${WORLD_FOLDER}:/config/.minetest/worlds/${WORLDNAME}" \
    -v "$(pwd)/logs:/config/.minetest/logs" \
    -p "${PORT}:${PORT}/udp" \
    --restart unless-stopped \
    "$IMAGE"

echo ""
echo "Server gestartet!"
echo "Verbinden mit: Server-IP:$PORT"
echo ""
echo "Logs anzeigen: docker logs -f $CONTAINER_NAME"
echo "Stoppen: docker stop $CONTAINER_NAME"
echo "Entfernen: docker rm $CONTAINER_NAME"
