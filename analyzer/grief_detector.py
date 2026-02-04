#!/usr/bin/env python3
"""
Grief-Detection Tool für Luanti Workshops

Analysiert Logfiles auf:
1. Multi-Account-Erkennung (IPs mit mehreren Usernamen)
2. Gruppen-basierte Grief-Erkennung (Abbau in fremden Bauzonen)
3. Zeitliche Analyse: Erkennt wenn jemand NACH Etablierung einer Zone dort abbaut
4. Follow-Mode für Live-Überwachung
"""

import re
import argparse
import time
from collections import defaultdict
from datetime import datetime
import statistics


class GriefDetector:
    def __init__(self, group_radius=100, min_place_count=20, min_group_time_minutes=30):
        self.group_radius = group_radius
        self.min_place_count = min_place_count
        self.min_group_time_minutes = min_group_time_minutes  # Min. Zeit um zur Gruppe zu gehören

        # IP/Account Tracking
        self.ip_to_users = defaultdict(set)
        self.user_to_ip = {}

        # Aktivitäts-Tracking mit Timestamps
        self.user_places = defaultdict(list)  # User → [(x, z, timestamp_str, datetime), ...]
        self.user_digs = defaultdict(list)    # User → [(x, z, timestamp_str, block, datetime), ...]

        # Berechnete Strukturen
        self.user_centers = {}      # User → (center_x, center_z)
        self.user_core_zones = {}   # User → (x1, z1, x2, z2)
        self.groups = []            # [{'members': set(), 'zone': ..., 'established_at': datetime}, ...]
        self.user_to_group = {}     # User → group_index

        # Grief-Tracking
        self.foreign_digs = defaultdict(list)

    def parse_timestamp(self, timestamp_str):
        """Parst Timestamp-String zu datetime"""
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

    def parse_line(self, line):
        """Parst eine einzelne Log-Zeile"""
        # Login
        join_match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):.*ACTION\[Server\]: (\w+) \[::ffff:(\d+\.\d+\.\d+\.\d+)\] joins game",
            line
        )
        if join_match:
            timestamp_str, user, ip = join_match.groups()
            self.ip_to_users[ip].add(user)
            self.user_to_ip[user] = ip
            return ('join', user, ip, timestamp_str)

        # Place
        place_match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):.*ACTION\[Server\]: (\w+) places node (\S+) at \(([-\d]+),([-\d]+),([-\d]+)\)",
            line
        )
        if place_match:
            timestamp_str, user, block, x, y, z = place_match.groups()
            dt = self.parse_timestamp(timestamp_str)
            self.user_places[user].append((int(x), int(z), timestamp_str, dt))
            return ('place', user, int(x), int(z), timestamp_str)

        # Dig
        dig_match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):.*ACTION\[Server\]: (\w+) digs (\S+) at \(([-\d]+),([-\d]+),([-\d]+)\)",
            line
        )
        if dig_match:
            timestamp_str, user, block, x, y, z = dig_match.groups()
            dt = self.parse_timestamp(timestamp_str)
            self.user_digs[user].append((int(x), int(z), timestamp_str, block, dt))
            return ('dig', user, int(x), int(z), timestamp_str, block)

        return None

    def get_ip_places(self):
        """Gruppiere alle Places nach IP (alle Accounts einer IP zusammen)"""
        ip_places = defaultdict(list)
        for user, places in self.user_places.items():
            ip = self.user_to_ip.get(user)
            if ip:
                ip_places[ip].extend(places)
        return ip_places

    def get_ip_digs(self):
        """Gruppiere alle Digs nach IP"""
        ip_digs = defaultdict(list)
        for user, digs in self.user_digs.items():
            ip = self.user_to_ip.get(user)
            if ip:
                for d in digs:
                    ip_digs[ip].append((*d, user))  # Füge Username hinzu für Tracking
        return ip_digs

    def calculate_user_centers(self):
        """Berechne Bau-Zentrum für jede IP (alle Accounts zusammen)"""
        self.user_centers = {}  # IP → (center_x, center_z)
        self.user_core_zones = {}  # IP → (x1, z1, x2, z2)
        self.ip_usernames = {}  # IP → set of usernames

        ip_places = self.get_ip_places()

        for ip, places in ip_places.items():
            # Sammle alle Usernames dieser IP
            self.ip_usernames[ip] = set(
                user for user in self.user_places.keys()
                if self.user_to_ip.get(user) == ip
            )

            if len(places) >= self.min_place_count:
                xs = sorted([p[0] for p in places])
                zs = sorted([p[1] for p in places])

                # Kern-Zone: mittlere 80% der Koordinaten (ignoriert Ausreißer)
                trim = max(1, len(xs) // 10)
                core_xs = xs[trim:-trim] if len(xs) > 2 * trim else xs
                core_zs = zs[trim:-trim] if len(zs) > 2 * trim else zs

                if core_xs and core_zs:
                    zone_width = max(core_xs) - min(core_xs)
                    zone_height = max(core_zs) - min(core_zs)

                    if zone_width <= 1000 and zone_height <= 1000:
                        self.user_centers[ip] = (
                            statistics.median(core_xs),
                            statistics.median(core_zs)
                        )
                        self.user_core_zones[ip] = (
                            min(core_xs), min(core_zs),
                            max(core_xs), max(core_zs)
                        )

    def cluster_groups(self):
        """Clustere IPs zu Gruppen basierend auf räumlicher Nähe"""
        self.groups = []
        self.user_to_group = {}  # IP → group_index

        ips = list(self.user_centers.keys())
        assigned = set()

        ip_places = self.get_ip_places()

        for ip in ips:
            if ip in assigned:
                continue

            # Neue Gruppe starten
            group_ips = {ip}
            center_x, center_z = self.user_centers[ip]

            # Finde alle IPs in Reichweite
            for other_ip in ips:
                if other_ip in assigned or other_ip == ip:
                    continue
                ox, oz = self.user_centers[other_ip]
                dist = abs(center_x - ox) + abs(center_z - oz)
                if dist <= self.group_radius:
                    group_ips.add(other_ip)

            # Gruppe registrieren
            group_idx = len(self.groups)
            for member_ip in group_ips:
                assigned.add(member_ip)
                self.user_to_group[member_ip] = group_idx

            # Sammle alle Usernames der Gruppe
            group_usernames = set()
            for member_ip in group_ips:
                group_usernames.update(self.ip_usernames.get(member_ip, set()))

            # Gruppen-Zone berechnen
            core_zones = [self.user_core_zones[m] for m in group_ips if m in self.user_core_zones]

            if core_zones:
                padding = 30
                zone = (
                    min(z[0] for z in core_zones) - padding,
                    min(z[1] for z in core_zones) - padding,
                    max(z[2] for z in core_zones) + padding,
                    max(z[3] for z in core_zones) + padding
                )

                # Berechne Etablierungs-Zeitpunkt aus allen Places der Gruppen-IPs
                all_places_in_zone = []
                for member_ip in group_ips:
                    for p in ip_places.get(member_ip, []):
                        x, z_coord, ts_str, dt = p
                        if dt and self.is_in_zone(x, z_coord, zone):
                            all_places_in_zone.append(dt)

                all_places_in_zone.sort()
                establish_threshold = max(10, self.min_place_count // 2)

                if len(all_places_in_zone) >= establish_threshold:
                    established_at = all_places_in_zone[establish_threshold - 1]
                elif all_places_in_zone:
                    established_at = all_places_in_zone[0]
                else:
                    established_at = None

                first_activity = all_places_in_zone[0] if all_places_in_zone else None
                last_activity = all_places_in_zone[-1] if all_places_in_zone else None

                self.groups.append({
                    'ips': group_ips,
                    'members': group_usernames,  # Usernames für Anzeige
                    'zone': zone,
                    'established_at': established_at,
                    'first_activity': first_activity,
                    'last_activity': last_activity,
                    'total_blocks': len(all_places_in_zone)
                })

    def assign_long_term_builders(self):
        """Füge IPs zu Gruppen hinzu, wenn sie dort lange genug gebaut haben"""
        ip_places = self.get_ip_places()

        # Finde alle IPs die noch keiner Gruppe zugeordnet sind
        unassigned_ips = set(ip_places.keys()) - set(self.user_to_group.keys())

        for ip in unassigned_ips:
            places = ip_places.get(ip, [])
            if not places:
                continue

            # Prüfe für jede Gruppe, ob diese IP dort lange genug gebaut hat
            for group_idx, group in enumerate(self.groups):
                zone = group['zone']

                # Finde alle Places dieser IP in dieser Zone
                places_in_zone = [
                    p for p in places
                    if p[3] and self.is_in_zone(p[0], p[1], zone)  # p[3] = datetime
                ]

                if len(places_in_zone) < 5:  # Mindestens 5 Blöcke in der Zone
                    continue

                # Berechne Zeitspanne der Aktivität in dieser Zone
                timestamps = sorted([p[3] for p in places_in_zone])
                first_time = timestamps[0]
                last_time = timestamps[-1]
                duration_minutes = (last_time - first_time).total_seconds() / 60

                # Wenn länger als min_group_time_minutes aktiv → zur Gruppe hinzufügen
                if duration_minutes >= self.min_group_time_minutes:
                    self.user_to_group[ip] = group_idx
                    group['ips'].add(ip)
                    group['members'].update(self.ip_usernames.get(ip, set()))
                    break  # IP kann nur zu einer Gruppe gehören

    def is_in_zone(self, x, z, zone):
        """Prüft ob Koordinate in Zone liegt"""
        x1, z1, x2, z2 = zone
        return x1 <= x <= x2 and z1 <= z <= z2

    def find_zone_group(self, x, z, exclude_group=None):
        """Findet welche Gruppe eine Zone besitzt"""
        for idx, group in enumerate(self.groups):
            if idx == exclude_group:
                continue
            if self.is_in_zone(x, z, group['zone']):
                return idx
        return None

    def analyze_digs(self):
        """Analysiere alle Digs auf Grief-Verdacht mit zeitlicher Komponente (IP-basiert)"""
        self.foreign_digs = defaultdict(list)  # IP → [digs]

        ip_digs = self.get_ip_digs()

        for ip, digs in ip_digs.items():
            ip_group = self.user_to_group.get(ip)

            for dig_data in digs:
                x, z, timestamp_str, block, dt, username = dig_data

                # In eigener Gruppe? → OK
                if ip_group is not None:
                    own_zone = self.groups[ip_group]['zone']
                    if self.is_in_zone(x, z, own_zone):
                        continue

                # In fremder Gruppe? → Verdächtig!
                victim_group = self.find_zone_group(x, z, exclude_group=ip_group)
                if victim_group is not None:
                    group_info = self.groups[victim_group]

                    # Zeitliche Analyse: War der Dig NACH der Etablierung?
                    is_after_established = False
                    time_diff_minutes = None

                    if dt and group_info['established_at']:
                        is_after_established = dt > group_info['established_at']
                        time_diff = dt - group_info['established_at']
                        time_diff_minutes = time_diff.total_seconds() / 60

                    self.foreign_digs[ip].append({
                        'x': x, 'z': z,
                        'timestamp': timestamp_str,
                        'datetime': dt,
                        'block': block,
                        'username': username,
                        'victim_group': victim_group,
                        'victim_members': group_info['members'],
                        'is_after_established': is_after_established,
                        'time_diff_minutes': time_diff_minutes
                    })

    def check_new_dig(self, user, x, z, timestamp_str, block):
        """Live-Check für Follow-Mode (IP-basiert)"""
        ip = self.user_to_ip.get(user)
        if not ip:
            return None

        ip_group = self.user_to_group.get(ip)
        dt = self.parse_timestamp(timestamp_str)

        if ip_group is not None:
            own_zone = self.groups[ip_group]['zone']
            if self.is_in_zone(x, z, own_zone):
                return None

        victim_group = self.find_zone_group(x, z, exclude_group=ip_group)
        if victim_group is not None:
            group_info = self.groups[victim_group]
            is_after = dt and group_info['established_at'] and dt > group_info['established_at']

            return {
                'user': user,
                'ip': ip,
                'x': x, 'z': z,
                'timestamp': timestamp_str,
                'block': block,
                'victim_group': victim_group,
                'victim_members': group_info['members'],
                'is_after_established': is_after
            }
        return None

    def print_report(self):
        """Gibt den Grief-Report aus"""
        print("\n" + "=" * 60)
        print("GRIEF DETECTION REPORT (mit zeitlicher Analyse)")
        print("=" * 60)

        # Multi-Accounts
        print("\n--- MULTI-ACCOUNT VERDACHT ---")
        multi = [(ip, users) for ip, users in self.ip_to_users.items() if len(users) > 1]
        if multi:
            for ip, users in sorted(multi, key=lambda x: -len(x[1])):
                print(f"\nIP: {ip} [{len(users)} Accounts]")
                print(f"  → {', '.join(sorted(users))}")
        else:
            print("Keine Multi-Accounts erkannt.")

        # Gruppen mit Zeitinfo
        print("\n--- ERKANNTE GRUPPEN ---")
        if self.groups:
            for idx, group in enumerate(self.groups):
                zone = group['zone']
                members = ', '.join(sorted(group['members']))
                print(f"\nGruppe {idx + 1}: {members}")
                print(f"  Zone: ({zone[0]}, {zone[1]}) bis ({zone[2]}, {zone[3]})")
                print(f"  Blöcke: {group['total_blocks']}")
                if group['established_at']:
                    print(f"  Etabliert: {group['established_at'].strftime('%H:%M:%S')}")
                if group['first_activity'] and group['last_activity']:
                    print(f"  Aktiv: {group['first_activity'].strftime('%H:%M')} - {group['last_activity'].strftime('%H:%M')}")
        else:
            print("Keine Gruppen erkannt (zu wenig Bauaktivität).")

        # Verdächtige Aktivitäten mit zeitlicher Analyse (IP-basiert)
        print("\n--- VERDÄCHTIGE AKTIVITÄTEN ---")
        if self.foreign_digs:
            # Sortiere nach Anzahl der "zeitlich verdächtigen" Digs
            def grief_score(item):
                ip, digs = item
                after_count = sum(1 for d in digs if d['is_after_established'])
                return (-after_count, -len(digs))

            for ip, digs in sorted(self.foreign_digs.items(), key=grief_score):
                usernames = self.ip_usernames.get(ip, set())
                ip_group = self.user_to_group.get(ip)
                group_info = f"Gruppe {ip_group + 1}" if ip_group is not None else "keine Gruppe"

                # Zähle zeitlich verdächtige Digs
                after_count = sum(1 for d in digs if d['is_after_established'])
                before_count = len(digs) - after_count

                # Verdachts-Level bestimmen
                if after_count > 10:
                    level = "🔴 HOCH"
                elif after_count > 0:
                    level = "🟡 MITTEL"
                else:
                    level = "🟢 NIEDRIG"

                names_str = ', '.join(sorted(usernames)) if usernames else "?"
                print(f"\nIP: {ip} ({names_str}) - {group_info} - Verdacht: {level}")
                print(f"  {len(digs)} Blöcke in fremden Zonen abgebaut:")
                print(f"    → {after_count}x NACH Etablierung (verdächtig)")
                print(f"    → {before_count}x VOR Etablierung (weniger verdächtig)")

                # Gruppiere nach Opfer-Gruppe
                by_victim = defaultdict(lambda: {'after': 0, 'before': 0, 'total': 0})
                for d in digs:
                    vg = d['victim_group']
                    by_victim[vg]['total'] += 1
                    if d['is_after_established']:
                        by_victim[vg]['after'] += 1
                    else:
                        by_victim[vg]['before'] += 1

                for vg, counts in sorted(by_victim.items(), key=lambda x: -x[1]['after']):
                    victims = ', '.join(sorted(self.groups[vg]['members']))
                    established = self.groups[vg]['established_at']
                    est_str = f" (etabliert {established.strftime('%H:%M')})" if established else ""
                    print(f"    Gruppe {vg + 1} ({victims}){est_str}:")
                    print(f"      {counts['after']}x nach / {counts['before']}x vor Etablierung")
        else:
            print("Keine verdächtigen Aktivitäten erkannt.")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Grief-Detection für Luanti Workshops (mit zeitlicher Analyse)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python grief_detector.py logs/06.log              # Standard-Report
  python grief_detector.py logs/06.log -f           # Follow-Mode (Live)
  python grief_detector.py logs/06.log --group-radius 150

Zeitliche Grief-Erkennung:
  - Gruppen werden als "etabliert" erkannt, wenn sie genug Blöcke gebaut haben
  - Digs NACH der Etablierung sind verdächtiger als Digs davor
  - Verdachts-Level: 🔴 HOCH (>10 Digs nach), 🟡 MITTEL (1-10), 🟢 NIEDRIG (0)
        """
    )
    parser.add_argument("logfile", help="Pfad zur Logdatei")
    parser.add_argument("-f", "--follow", action="store_true",
                        help="Follow-Mode: Kontinuierliche Überwachung")
    parser.add_argument("--group-radius", type=int, default=100,
                        help="Max. Distanz für Gruppen-Clustering (Default: 100)")
    parser.add_argument("--min-places", type=int, default=20,
                        help="Min. Blöcke um User einer Zone zuzuordnen (Default: 20)")
    args = parser.parse_args()

    detector = GriefDetector(
        group_radius=args.group_radius,
        min_place_count=args.min_places
    )

    # Initiales Parsen
    print(f"Analysiere {args.logfile}...")
    with open(args.logfile, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            detector.parse_line(line)
        file_pos = f.tell()

    # Analyse
    detector.calculate_user_centers()
    detector.cluster_groups()
    detector.assign_long_term_builders()
    detector.analyze_digs()
    detector.print_report()

    # Follow-Mode
    if args.follow:
        print("\n" + "=" * 60)
        print("FOLLOW-MODE AKTIV - Warte auf neue Einträge...")
        print("(Strg+C zum Beenden)")
        print("=" * 60 + "\n")

        try:
            with open(args.logfile, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(file_pos)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.2)
                        continue

                    result = detector.parse_line(line)
                    if result and result[0] == 'dig':
                        _, user, x, z, timestamp, block = result
                        alert = detector.check_new_dig(user, x, z, timestamp, block)
                        if alert:
                            victims = ', '.join(sorted(alert['victim_members']))
                            after_marker = " [NACH ETABLIERUNG!]" if alert['is_after_established'] else ""
                            print(f"[ALERT] {timestamp} - {user} baut ab in Zone von: {victims}{after_marker}")
                            print(f"         Position: ({x}, {z}), Block: {block}")

                    if result and result[0] == 'join':
                        _, user, ip, timestamp = result
                        if len(detector.ip_to_users[ip]) > 1:
                            others = detector.ip_to_users[ip] - {user}
                            print(f"[WARN] {timestamp} - {user} (IP: {ip}) - Auch bekannt als: {', '.join(others)}")
        except KeyboardInterrupt:
            print("\n\nFollow-Mode beendet.")


if __name__ == "__main__":
    main()
