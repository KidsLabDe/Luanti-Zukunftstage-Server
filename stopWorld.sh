#!/bin/bash
# Stoppt einen Zukunftstage-Server
#
# Verwendung:
#   ./stopWorld.sh <weltordner>
#   ./stopWorld.sh all  (stoppt alle)

set -e

WORLD_FOLDER="${1}"

if [ -z "$WORLD_FOLDER" ]; then
    echo "Laufende Server:"
    docker ps --filter "name=zfn_" --format "  {{.Names}}"
    echo ""
    read -p "Welchen Server stoppen? (Name oder 'all'): " WORLD_FOLDER
fi

if [ "$WORLD_FOLDER" = "all" ]; then
    echo "Stoppe alle Zukunftstage Server..."
    docker ps --filter "name=zfn_" -q | xargs -r docker stop
    docker ps --filter "name=zfn_" -a -q | xargs -r docker rm
    echo "Alle Server gestoppt und entfernt."
else
    CONTAINER_NAME="zfn_$(echo $WORLD_FOLDER | tr -cd '[:alnum:]_-')"
    echo "Stoppe $CONTAINER_NAME..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "Server gestoppt."
fi
