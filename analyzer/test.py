import time
import re
import subprocess
import argparse
import os

# Reguläre Ausdrücke (angepasst an das Standard-Luanti/Minetest Format)
# Loggt IP beim Login: "ACTION[Server]: Player name [192.168.1.50] joins game"
join_pattern = re.compile(r"ACTION\[Server\]: (\w+) \[([0-9.]+)\] joins game")
tnt_pattern = re.compile(r"ACTION\[Server\]: (\w+) places node mcl_tnt:tnt")
invis_pattern = re.compile(r"ACTION\[Server\]: (\w+) activates mcl_potions:invisibility_splash")

player_ips = {}

def play_remote(ip, filename):
    """Überträgt die Sounddatei per SCP und spielt sie per SSH ab."""
    print(f"--> [ALARM] Sende {filename} an {ip}...")
    try:
        # Ersetze 'user' durch den echten Benutzernamen des Ziel-PCs
        user = "user" 
        # Datei kopieren
        subprocess.run(["scp", filename, f"{user}@{ip}:/tmp/{filename}"], check=True, capture_output=True)
        # Datei abspielen und danach löschen
        # mpg123 muss auf dem Ziel-PC installiert sein
        subprocess.run(["ssh", f"{user}@{ip}", f"mpg123 /tmp/{filename} && rm /tmp/{filename}"], 
                       start_new_session=True)
    except Exception as e:
        print(f"Fehler bei SSH-Verbindung zu {ip}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", help="Pfad zur Luanti Logdatei")
    parser.add_argument("--test", action="store_true", help="Nur Aktionen vom Benutzer 'tester' verarbeiten")
    args = parser.parse_args()

    print('test: ',args.test)
main()
