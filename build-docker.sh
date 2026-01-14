#!/bin/bash
# Baut das Zukunftstage Docker Image
#
# Das Image enthält:
# - Alle Mods (worldedit, travelnet, world2minetest, etc.)
# - Alle Games (mineclonia, antigrief, minetest)
# - Workshop-Konfiguration (Anti-Grief, Creative Mode, etc.)
#
# Nach dem Build nur noch Welt mounten und starten!

set -e

IMAGE_NAME="ghcr.io/kidslabde/luanti-zukunftstage-server"
IMAGE_TAG="${1:-latest}"

echo "Baue Docker Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo ""
echo "Image erfolgreich gebaut: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "Verwendung:"
echo "  ./startWorld.sh <weltname> <port>"
echo ""
echo "Beispiel:"
echo "  ./startWorld.sh 02-koeln 30102"
