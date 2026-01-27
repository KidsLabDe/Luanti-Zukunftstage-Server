import time
import re
import subprocess
import argparse
import os

# Robustes IP-Muster
join_pattern = re.compile(r"ACTION\[Server\]: (\w+) \[(?:.*:)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\] joins game")
tnt_pattern = re.compile(r"ACTION\[Server\]: (\w+) places node mcl_tnt:tnt")
invis_pattern = re.compile(r"ACTION\[Server\]: (\w+) activates mcl_potions:invisibility_splash")

player_ips = {}
# Hier merken wir uns: { "192.168.23.105": True }
already_uploaded = set()

def play_remote(ip, filename):
    user = "kidslab"
    pw = "kidslab"
    
    # Pfad auf dem Zielrechner (wir löschen sie NICHT mehr sofort, damit sie da bleibt)
    remote_path = f"/home/{user}/{filename}"
    
    try:
        # 1. Nur hochladen, wenn noch nicht geschehen
        if ip not in already_uploaded:
            print(f"--> [Upload] Übertrage {filename} einmalig an {ip}...")
            subprocess.run([
                "sshpass", "-p", pw, "scp", "-o", "StrictHostKeyChecking=no", 
                filename, f"{user}@{ip}:{remote_path}"
            ], check=True, capture_output=True)
            already_uploaded.add(ip)

        # 2. Nur noch den Abspielbefehl senden (extrem schnell)
        # Wir setzen die Lautstärke und spielen ab
        remote_cmd = f"amixer set Master 80% > /dev/null && mpg123 -q {remote_path} && amixer set Master 20% > /dev/null"
        
        print(f"--> [ALARM] Trigger {filename} auf {ip}")
        subprocess.run([
            "sshpass", "-p", pw, "ssh", "-o", "StrictHostKeyChecking=no", 
            f"{user}@{ip}", remote_cmd
        ], start_new_session=True)
        
    except Exception as e:
        print(f"Fehler bei {ip}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", help="Pfad zur action.log")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    # Initialer Scan...
    with open(args.logfile, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = join_pattern.search(line)
            if match:
                name, ip = match.groups()
                player_ips[name.lower()] = ip
        f.seek(0, os.SEEK_END)
        last_pos = f.tell()

    print(f"Monitoring läuft. Bekannte IPs: {list(player_ips.values())}")

    with open(args.logfile, "r", encoding='utf-8', errors='ignore') as f:
        f.seek(last_pos)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1) # Kürzere Pause für schnellere Reaktion
                continue

            # Login Check
            join_match = join_pattern.search(line)
            if join_match:
                name, ip = join_match.groups()
                player_ips[name.lower()] = ip

            # Aktions Check
            t_match = tnt_pattern.search(line)
            i_match = invis_pattern.search(line)
            
            match = t_match or i_match
            if match:
                p_name = match.group(1)
                if args.test and p_name.lower() != "tester":
                    continue

                target_ip = player_ips.get(p_name.lower())
                if target_ip:
                    # Wir spielen tnt.mp3 oder invisible.mp3
                    play_remote(target_ip, "tnt.mp3" if t_match else "invisible.mp3")

if __name__ == "__main__":
    main()
