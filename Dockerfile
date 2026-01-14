# Zukunftstage Luanti Server
# Enthält alle Mods, Games und Konfiguration
# Nur noch Welt-Verzeichnis mounten und starten

FROM ghcr.io/linuxserver/luanti:latest

# Mods kopieren
COPY mods/ /config/.minetest/mods/

# Games kopieren
COPY games/ /config/.minetest/games/

# Workshop-Konfiguration als Standard
COPY main-config/workshop.conf /config/.minetest/main-config/minetest.conf

# Leeres worlds Verzeichnis erstellen (wird als Volume gemountet)
RUN mkdir -p /config/.minetest/worlds

# Logs Verzeichnis
RUN mkdir -p /config/.minetest/logs

# Berechtigungen für linuxserver.io Image
RUN chown -R abc:abc /config/.minetest
