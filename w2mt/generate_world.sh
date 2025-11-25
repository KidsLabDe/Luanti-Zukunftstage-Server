#!/bin/bash

export MINETEST_GAME_PATH=/opt/zfn-server-docker

# Variablen deklarieren
name=""
koordinate1=""
koordinate2=""

# Eingabe des Projektnamens
echo "Bitte geben Sie den Namen des Projekts ein:"
read name

# Eingabe der ersten Koordinate
echo "Bitte geben Sie die erste Koordinate ein (z.B. 10.0,50.0):"
read koordinate1

# Eingabe der zweiten Koordinate
echo "Bitte geben Sie die zweite Koordinate ein (z.B. 11.0,51.0):"
read koordinate2

# Python-Skript mit Variablen aufrufen
python3 w2mt.py -p "$name" -a "$koordinate1,$koordinate2" -g "antigrief" -b "leveldb"

echo "Das Python-Skript wurde erfolgreich ausgeführt."

