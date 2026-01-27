import time
import re
import subprocess
import argparse
import os

# Regulärer Ausdruck für den Login (berücksichtigt nun auch ::ffff: Präfixe und die Spielerliste)
# Beispiel: 2026-01-27 11:42:55: ACTION[Server]: tester [::ffff:192.168.23.105] joins game.
join_pattern = re.compile(r"ACTION\[Server\]: (\w+) \[(?:.*:)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\] joins game")

# Reguläre Ausdrücke für die Aktionen
tnt_pattern = re.compile(r"ACTION\[Server\]: (\w+) places node mcl_tnt:tnt")
invis_pattern = re.compile(r"ACTION\[Server\]: (\w+) activates mcl_potions:invisibility_splash")

player_ips = {}

def play_remote(ip, filename):
    """Überträgt die Sounddatei per SCP und spielt sie per SSH ab (mit Passwort-Auth)."""
    user = "kidslab"
    pw = "kidslab"
    
    print(f"--> [ALARM] Sende {filename} an {ip}...")
    
    try:
        # SCP mit Passwort (Datei nach /tmp kopieren)
        scp_cmd = ["sshpass", "-p", pw, "scp", "-o", "StrictHostKeyChecking=no", 
                   filename, f"{user}@{ip}:/tmp/{filename}"]
        subprocess.run(scp_cmd, check=True, capture_output=True)
        
        # SSH mit Passwort (Abspielen und Löschen)
        # Wir nutzen mpg123 - falls nicht vorhanden, durch paplay ersetzen
        ssh_cmd = ["sshpass", "-p", pw, "ssh", "-o", "StrictHostKeyChecking=no", 
                   f"{user}@{ip}", f"mpg123 /tmp/{filename} && rm /tmp/{filename}"]
        subprocess.run(ssh_cmd, start_new_session=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Verbindung zu {ip}: {e}")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

def main():
    parser = argparse.ArgumentParser(description="Minetest Sound-Alarm System")
    parser.add_argument("logfile", help="Pfad zur Luanti/Minetest Logdatei")
    parser.add_argument("--test", action="store_true", help="Nur Aktionen vom Benutzer 'tester' verarbeiten")
    args = parser.parse_args()

    if not os.path.exists(args.logfile):
        print(f"Fehler: Datei {args.logfile} nicht gefunden.")
        return

    # --- SCHRITT 1: Bestehende Logdatei nach IPs scannen ---
    print("Scanne Logdatei nach bekannten Spieler-IPs...")
    with open(args.logfile, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            join_match = join_pattern.search(line)
            if join_match:
                name, ip = join_match.groups()
                player_ips[name.lower()] = ip
        
        # Aktuelle Dateigröße merken, um nur neue Zeilen zu lesen
        f.seek(0, os.SEEK_END)
        last_pos = f.tell()

    print(f"Initialisierung fertig. {len(player_ips)} IPs bekannt.")
    if args.test:
        print("!!! TESTMODUS AKTIV: Reagiere nur auf 'tester' !!!")

    # --- SCHRITT 2: Live-Überwachung ---
    print("Warte auf Aktionen...")
    try:
        with open(args.logfile, "r", encoding='utf-8', errors='ignore') as f:
            f.seek(last_pos)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue

                # Neue Logins erfassen
                join_match = join_pattern.search(line)
                if join_match:
                    name, ip = join_match.groups()
                    player_ips[name.lower()] = ip
                    print(f"[Login] {name} verbunden unter {ip}")

                # TNT oder Unsichtbarkeit prüfen
                tnt_match = tnt_pattern.search(line)
                invis_match = invis_pattern.search(line)

                match = tnt_match or invis_match
                if match:
                    p_name = match.group(1)
                    
                    # Filter für Testmodus
                    if args.test and p_name.lower() != "tester":
                        continue

                    action_file = "tnt.mp3" if tnt_match else "invisible.mp3"
                    target_ip = player_ips.get(p_name.lower())

                    if target_ip:
                        print(f"EVENT: {p_name} -> {action_file} auf Ziel-IP {target_ip}")
                        play_remote(target_ip, action_file)
                    else:
                        print(f"Aktion von {p_name} erkannt, aber IP ist unbekannt.")
    except KeyboardInterrupt:
        print("\nÜberwachung beendet.")

if __name__ == "__main__":
    main()
