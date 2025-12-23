# Luanti Zukunftstage Server

## Über das Projekt

Dieses Repository enthält das Server-Setup für die **Digitalen Zukunftstage** und **Zukunftsnächte**, ein Projekt der [Bayerischen Landeszentrale für politische Bildungsarbeit (blz)](https://www.blz.bayern.de/digitale-zukunftstage.html) in Kooperation mit [KidsLab.de](https://zukunftsnacht.de/).

Das Kernkonzept besteht aus interaktiven Workshops, in denen Schülerinnen und Schüler (ab der 8. Klasse) die Zukunft ihrer eigenen Stadt gestalten. In einer spielerischen Umgebung, die auf Minetest (ähnlich wie Minecraft) basiert, errichten sie virtuelle Modelle ihrer Ideen – von Grünflächen über Jugendzentren bis hin zu nachhaltigen Verkehrskonzepten.

Diese digitalen Kreationen dienen als Grundlage für Diskussionen mit lokalen Entscheidungsträgern, fördern die politische Teilhabe und zeigen den Jugendlichen, dass ihre Stimme bei der Gemeindeentwicklung zählt.

## Setup und Nutzung

Hier wird beschrieben, wie eine neue Welt aus Geodaten generiert und der Server mit Docker gestartet wird.

### Voraussetzungen

-   **Docker** und **Docker Compose**: Zur Ausführung des Minetest-Servers in einem Container.
-   **Python 3** und `pip`: Wird für die Welt-Generierungsskripte benötigt.
-   **Git**: Zur Verwaltung des Repositories.

### 1. Welt generieren (mit `w2mt`)

Das `w2mt`-Skript (`world2minetest`) generiert eine Minetest-Welt basierend auf echten Geodaten von OpenStreetMap.

1.  **In das `w2mt`-Verzeichnis wechseln:**
    ```bash
    cd w2mt/
    ```

2.  **Python-Abhängigkeiten installieren:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Generierungs-Skript ausführen:**
    Das Skript `generate_world.sh` ist ein einfacher Wrapper, der die notwendigen Parameter abfragt.
    ```bash
    ./generate_world.sh
    ```
    Das Skript fragt dich nach:
    -   Einem **Projektnamen** (z.B. `02-Muenchen`).
    -   Zwei **Koordinaten**, die ein Rechteck auf der Weltkarte aufspannen. Diese können z.B. von OpenStreetMap entnommen werden (Klick auf "Export" -> Bereich manuell auswählen).

    Das Skript ruft dann das Kernskript `w2mt.py` auf, das die Geodaten herunterlädt und die Welt-Map (`map.dat`) im Verzeichnis `worlds/<projektname>/world2minetest/` ablegt.

### 2. Server starten (mit Docker)

Das `startWorkshop.sh`-Skript vereinfacht das Starten einer spezifischen Welt.

1.  **Skript ausführbar machen (falls noch nicht geschehen):**
    ```bash
    chmod +x startWorkshop.sh
    ```

2.  **Skript ausführen:**
    ```bash
    ./startWorkshop.sh
    ```

3.  **Welt auswählen:**
    Das Skript listet die verfügbaren Welt-Verzeichnisse auf und fragt, welche Welt gestartet werden soll (z.B. `01`, `02`).

    Im Hintergrund tut das Skript Folgendes:
    - Es kopiert die spezifische `map.dat` der ausgewählten Welt in das von Docker genutzte Mod-Verzeichnis.
    - Es startet den Docker-Container über `docker compose -f workshop.yaml up`.

Der Minetest-Server ist nun unter Port `30000` (UDP) erreichbar.

## Zusammenfassung der Entwicklungshistorie

Die Analyse der Commits zeichnet ein klares Bild der Entwicklung dieses Servers:

#### Phase 1: Das Fundament (vor 4 Wochen)
-   Das Projekt wurde mit einer komplexen Docker-Architektur ins Leben gerufen, mit dem klaren Ziel, das Spiel **Mineclonia** mit dem Kartengenerator **world2minetest** zu kombinieren. Von Anfang an wurden viele Welten und eine große Mod-Sammlung eingeplant.

#### Phase 2: Erste Inhalte & Konfiguration (vor 11-12 Tagen)
-   Die erste konkrete Welt ("Augsburg") wurde dem Projekt hinzugefügt.
-   Es wurden die notwendigen Konfigurationen vorgenommen, um `world2minetest` anzuweisen, Mineclonias eigenen Kartengenerator zu deaktivieren, damit sie sich nicht gegenseitig stören.
-   Die Projektstruktur wurde vereinfacht, indem die Weltdaten und das Mineclonia-Spiel direkt in das Haupt-Repository integriert wurden, anstatt sie als Submodule zu verwalten. Dies machte das Projekt in sich geschlossener.
-   Eine `CLAUDE.md`-Datei wurde hinzugefügt, um die Entwicklung mit KI-Unterstützung zu erleichtern.

#### Phase 3: Visuelle Anpassung & Optimierung (letzte 24 Stunden)
-   Der `world2minetest`-Generator wurde tiefgreifend überarbeitet, um anstelle von Standard-Minetest-Blöcken spezifische, optisch passende Blöcke aus Mineclonia zu verwenden.
-   Die Augsburg-Welt wurde daraufhin neu generiert, um diese visuellen Verbesserungen anzuwenden.
-   Es wurden umfangreiche **Anti-Grief-Maßnahmen** implementiert, um das Spiel für den Einsatz in Workshops (z.B. mit Kindern und Jugendlichen) sicherer zu machen. Störende Elemente wie Lava, Monster und Explosionen können nun zentral deaktiviert werden.
-   Zuletzt wurden kleinere Fehler und Inkonsistenzen behoben.

**Fazit:** Ausgehend von einem funktionierenden Prototyp wurde der Server schrittweise zu einem robusten, maßgeschneiderten System für Mineclonia-Workshops weiterentwickelt. Die Prioritäten lagen dabei auf struktureller Vereinfachung, visueller Anpassung an Mineclonia und der Schaffung einer sicheren, kontrollierbaren Umgebung für die Teilnehmer.