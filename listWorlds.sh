#!/bin/bash
# Zeigt alle laufenden Zukunftstage-Server an

echo "Laufende Zukunftstage Server:"
echo ""
docker ps --filter "name=zfn_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
