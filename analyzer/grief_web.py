#!/usr/bin/env python3
"""
Web-Oberfläche für Grief-Detection Tool

Startet einen kleinen Webserver der die Grief-Analyse als Webseite anzeigt.
"""

import argparse
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from collections import defaultdict
from datetime import datetime

# Import grief_detector from same directory
try:
    from grief_detector import GriefDetector
except ImportError:
    from analyzer.grief_detector import GriefDetector


class GriefWebHandler(SimpleHTTPRequestHandler):
    detector = None
    logfile = None
    group_radius = 100
    min_places = 20

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))

        elif parsed.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Parse time filter from query params
            query = parse_qs(parsed.query)
            time_start = query.get('start', [None])[0]
            time_end = query.get('end', [None])[0]

            data = self.get_analysis_data(time_start, time_end)
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        else:
            self.send_error(404)

    def get_analysis_data(self, time_start=None, time_end=None):
        """Führt Analyse durch und gibt JSON-Daten zurück"""
        detector = GriefDetector(
            group_radius=self.group_radius,
            min_place_count=self.min_places
        )

        # Parse logfile und sammle Zeitinfo
        all_timestamps = []
        try:
            with open(self.logfile, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    result = detector.parse_line(line)
                    # Sammle alle Timestamps für den Zeitstrahl
                    if result and len(result) >= 4:
                        ts_str = result[-1] if result[0] == 'join' else result[4] if len(result) > 4 else None
                        if ts_str:
                            try:
                                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                                all_timestamps.append(dt)
                            except:
                                pass
        except Exception as e:
            return {'error': str(e)}

        # Berechne Zeitbereich
        if all_timestamps:
            log_start = min(all_timestamps)
            log_end = max(all_timestamps)
        else:
            log_start = log_end = datetime.now()

        # Parse Filter-Zeiten
        filter_start = None
        filter_end = None
        if time_start:
            try:
                filter_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
            except:
                pass
        if time_end:
            try:
                filter_end = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")
            except:
                pass

        # WICHTIG: Gruppen IMMER aus gesamtem Log berechnen (stabile Gruppenzugehörigkeit)
        detector.calculate_user_centers()
        detector.cluster_groups()
        detector.assign_long_term_builders()

        # Zeitfilter NUR auf Digs anwenden (nicht auf Places/Gruppen)
        if filter_start or filter_end:
            for user in list(detector.user_digs.keys()):
                detector.user_digs[user] = [
                    d for d in detector.user_digs[user]
                    if (not filter_start or (d[4] and d[4] >= filter_start)) and
                       (not filter_end or (d[4] and d[4] <= filter_end))
                ]

        detector.analyze_digs()

        # Multi-Accounts
        multi_accounts = []
        for ip, users in detector.ip_to_users.items():
            if len(users) > 1:
                multi_accounts.append({
                    'ip': ip,
                    'users': sorted(users),
                    'count': len(users)
                })
        multi_accounts.sort(key=lambda x: -x['count'])

        # Gruppen mit Koordinaten und Zeitinfo
        groups = []
        for idx, group in enumerate(detector.groups):
            zone = group['zone']
            members = sorted(group['members'])

            center_x = (zone[0] + zone[2]) / 2
            center_z = (zone[1] + zone[3]) / 2

            # Sammle alle Place-Koordinaten der Gruppe (für 2D-Visualisierung)
            all_places = []
            for member in group['members']:
                if member in detector.user_places:
                    all_places.extend(detector.user_places[member])

            # Sampling: bei vielen Blöcken nur jeden n-ten nehmen
            max_points = 2000
            if len(all_places) > max_points:
                step = len(all_places) // max_points
                all_places = all_places[::step]

            # Nur x,z Koordinaten für die Karte
            place_coords = [{'x': p[0], 'z': p[1]} for p in all_places]

            groups.append({
                'id': idx + 1,
                'ips': sorted(group.get('ips', set())),
                'members': members,
                'zone': {
                    'x1': zone[0], 'z1': zone[1],
                    'x2': zone[2], 'z2': zone[3]
                },
                'center': {'x': center_x, 'z': center_z},
                'total_blocks': group.get('total_blocks', 0),
                'places': place_coords,
                'established_at': group['established_at'].strftime('%H:%M:%S') if group.get('established_at') else None,
                'first_activity': group['first_activity'].strftime('%H:%M') if group.get('first_activity') else None,
                'last_activity': group['last_activity'].strftime('%H:%M') if group.get('last_activity') else None
            })

        # Verdächtige Aktivitäten mit zeitlicher Analyse (IP-basiert)
        suspicious = []
        for ip, digs in detector.foreign_digs.items():
            usernames = detector.ip_usernames.get(ip, set())
            ip_group = detector.user_to_group.get(ip)

            after_count = sum(1 for d in digs if d.get('is_after_established', False))
            before_count = len(digs) - after_count

            by_victim = {}
            for d in digs:
                vg = d['victim_group']
                if vg not in by_victim:
                    by_victim[vg] = {
                        'victim_group': vg + 1,
                        'victim_members': sorted(detector.groups[vg]['members']),
                        'count': 0,
                        'after_count': 0,
                        'before_count': 0,
                        'locations': [],
                        'established_at': detector.groups[vg]['established_at'].strftime('%H:%M') if detector.groups[vg].get('established_at') else None
                    }
                by_victim[vg]['count'] += 1
                if d.get('is_after_established', False):
                    by_victim[vg]['after_count'] += 1
                else:
                    by_victim[vg]['before_count'] += 1
                by_victim[vg]['locations'].append({
                    'x': d['x'], 'z': d['z'],
                    'is_after': d.get('is_after_established', False)
                })

            if after_count > 10:
                level = 'high'
            elif after_count > 0:
                level = 'medium'
            else:
                level = 'low'

            suspicious.append({
                'ip': ip,
                'usernames': sorted(usernames),
                'user_group': ip_group + 1 if ip_group is not None else None,
                'total_digs': len(digs),
                'after_count': after_count,
                'before_count': before_count,
                'level': level,
                'targets': sorted(by_victim.values(), key=lambda x: -x['after_count'])
            })

        suspicious.sort(key=lambda x: (-x['after_count'], -x['total_digs']))

        # Berechne Bounds für Karte
        all_coords = []
        for group in detector.groups:
            zone = group['zone']
            all_coords.extend([(zone[0], zone[1]), (zone[2], zone[3])])

        if all_coords:
            min_x = min(c[0] for c in all_coords)
            max_x = max(c[0] for c in all_coords)
            min_z = min(c[1] for c in all_coords)
            max_z = max(c[1] for c in all_coords)
        else:
            min_x, max_x, min_z, max_z = 0, 100, 0, 100

        return {
            'logfile': self.logfile,
            'time_range': {
                'start': log_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end': log_end.strftime('%Y-%m-%d %H:%M:%S'),
                'start_display': log_start.strftime('%H:%M'),
                'end_display': log_end.strftime('%H:%M')
            },
            'filter': {
                'start': filter_start.strftime('%Y-%m-%d %H:%M:%S') if filter_start else None,
                'end': filter_end.strftime('%Y-%m-%d %H:%M:%S') if filter_end else None
            },
            'multi_accounts': multi_accounts,
            'groups': groups,
            'suspicious': suspicious,
            'bounds': {
                'min_x': min_x, 'max_x': max_x,
                'min_z': min_z, 'max_z': max_z
            },
            'stats': {
                'total_users': len(detector.user_to_ip),
                'total_groups': len(detector.groups),
                'total_suspicious': len(suspicious),
                'high_risk': sum(1 for s in suspicious if s['level'] == 'high'),
                'medium_risk': sum(1 for s in suspicious if s['level'] == 'medium')
            }
        }

    def get_html(self):
        return '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Grief Detection - Workshop Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }
        h1 { color: #00d4ff; margin-bottom: 5px; }
        .subtitle { color: #888; margin-bottom: 10px; font-size: 14px; }

        /* Zeitfilter */
        .time-filter {
            background: #16213e;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            border: 1px solid #0f3460;
        }
        .time-filter h3 {
            color: #00d4ff;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .time-slider-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .time-label-box {
            text-align: center;
            min-width: 70px;
        }
        .time-label-title {
            font-size: 10px;
            color: #666;
            display: block;
        }
        .time-label {
            font-family: monospace;
            font-size: 14px;
            color: #888;
        }
        .time-slider {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 5px;
            position: relative;
        }
        .slider-values {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .slider-value {
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            color: #00d4ff;
            background: #0f3460;
            padding: 4px 10px;
            border-radius: 5px;
        }
        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 24px;
            background: linear-gradient(to right, #0f3460 0%, #00d4ff 50%, #0f3460 100%);
            border-radius: 5px;
            cursor: pointer;
            margin: 2px 0;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #00d4ff;
            cursor: pointer;
            border: 3px solid #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        input[type="range"]::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #00d4ff;
            cursor: pointer;
            border: 3px solid #fff;
        }
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .filter-buttons button {
            padding: 6px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 13px;
        }
        .btn-apply { background: #00d4ff; color: #000; }
        .btn-reset { background: #0f3460; color: #fff; }
        .btn-refresh { background: #00d4ff; color: #000; }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }

        .card {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        .card h2 {
            color: #00d4ff;
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #0f3460;
        }
        .card h2 .count {
            background: #e94560;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 14px;
            margin-left: 10px;
        }
        .card h2 .count.ok { background: #00d4ff; }

        .multi-account {
            background: #1a1a2e;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #e94560;
        }
        .multi-account .ip { font-family: monospace; color: #e94560; font-weight: bold; }
        .multi-account .users { color: #aaa; margin-top: 5px; }

        .suspicious {
            background: #1a1a2e;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .suspicious.high { border-left: 4px solid #ff4444; }
        .suspicious.medium { border-left: 4px solid #ffaa00; }
        .suspicious.low { border-left: 4px solid #44aa44; }
        .suspicious .header { display: flex; justify-content: space-between; align-items: center; }
        .suspicious .ip-info { font-weight: bold; font-family: monospace; }
        .suspicious.high .ip-info { color: #ff4444; }
        .suspicious.medium .ip-info { color: #ffaa00; }
        .suspicious.low .ip-info { color: #44aa44; }
        .suspicious .level { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
        .suspicious.high .level { background: #ff4444; }
        .suspicious.medium .level { background: #ffaa00; color: #000; }
        .suspicious.low .level { background: #44aa44; }
        .suspicious .details { color: #888; font-size: 13px; margin-top: 5px; }
        .suspicious .usernames { color: #aaa; font-size: 12px; margin-top: 3px; }
        .suspicious .time-breakdown { display: flex; gap: 15px; margin-top: 8px; font-size: 13px; }
        .suspicious .after { color: #ff6b6b; }
        .suspicious .before { color: #888; }
        .suspicious .target {
            background: #0f3460;
            padding: 8px 10px;
            border-radius: 5px;
            margin-top: 8px;
            font-size: 13px;
        }
        .suspicious .target .victim { color: #00d4ff; }

        .map-container { background: #1a1a2e; border-radius: 8px; padding: 10px; position: relative; }
        #map { width: 100%; height: 400px; background: #0d1117; border-radius: 5px; cursor: grab; }
        #map:active { cursor: grabbing; }
        .map-controls { position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 5px; }
        .map-controls button {
            width: 32px; height: 32px; border: none; border-radius: 5px;
            background: #0f3460; color: #fff; font-size: 18px; cursor: pointer;
        }
        .map-controls button:hover { background: #00d4ff; color: #000; }
        .map-legend { margin-top: 10px; font-size: 12px; color: #888; }
        .map-legend span { margin-right: 15px; }

        /* Gruppen-Info Popup */
        #group-popup {
            display: none;
            position: absolute;
            background: #16213e;
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 15px;
            min-width: 250px;
            max-width: 350px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            z-index: 100;
        }
        #group-popup .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #0f3460;
        }
        #group-popup .popup-title { font-weight: bold; font-size: 16px; }
        #group-popup .popup-close {
            background: none; border: none; color: #888; font-size: 20px; cursor: pointer;
        }
        #group-popup .popup-close:hover { color: #ff4444; }
        #group-popup .popup-row { margin: 8px 0; font-size: 13px; }
        #group-popup .popup-label { color: #888; display: block; font-size: 11px; margin-bottom: 2px; }
        #group-popup .popup-value { color: #fff; }
        #group-popup .popup-members { color: #00d4ff; }

        .group-item {
            background: #1a1a2e;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #00d4ff;
        }
        .group-item .name { font-weight: bold; color: #00d4ff; }
        .group-item .members { color: #aaa; margin-top: 5px; }
        .group-item .ips { color: #666; font-size: 11px; font-family: monospace; margin-top: 3px; }
        .group-item .info { display: flex; gap: 15px; font-size: 12px; color: #666; margin-top: 8px; flex-wrap: wrap; }
        .group-item .info span { background: #0f3460; padding: 2px 8px; border-radius: 4px; }

        .empty { color: #666; font-style: italic; padding: 20px; text-align: center; }

        .stats { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
        .stat { background: #16213e; padding: 15px 25px; border-radius: 10px; text-align: center; min-width: 100px; }
        .stat .value { font-size: 28px; font-weight: bold; color: #00d4ff; }
        .stat .label { font-size: 12px; color: #888; margin-top: 5px; }
        .stat.danger .value { color: #ff4444; }
        .stat.warning .value { color: #ffaa00; }
    </style>
</head>
<body>
    <h1>Grief Detection Monitor</h1>
    <p class="subtitle">Logfile: <span id="logfile">-</span></p>

    <div class="time-filter">
        <h3>Zeitfilter <span id="filter-info" style="color:#888;font-weight:normal;font-size:12px;margin-left:10px;"></span></h3>
        <div class="time-slider-container">
            <div class="time-label-box">
                <span class="time-label-title">Log Start</span>
                <span class="time-label" id="log-start">--:--</span>
            </div>
            <div class="time-slider">
                <div class="slider-values">
                    <span id="slider-start-value" class="slider-value">--:--</span>
                    <span id="slider-end-value" class="slider-value">--:--</span>
                </div>
                <input type="range" id="slider-start" min="0" max="100" value="0" oninput="updateSliderDisplay()">
                <input type="range" id="slider-end" min="0" max="100" value="100" oninput="updateSliderDisplay()">
            </div>
            <div class="time-label-box">
                <span class="time-label-title">Log Ende</span>
                <span class="time-label" id="log-end">--:--</span>
            </div>
        </div>
        <div class="filter-buttons">
            <button class="btn-apply" onclick="applyFilter()">Filter anwenden</button>
            <button class="btn-reset" onclick="resetFilter()">Zurücksetzen</button>
            <button class="btn-refresh" onclick="loadData()">Neu laden</button>
        </div>
    </div>

    <div class="stats" id="stats"></div>

    <div class="grid">
        <div class="card">
            <h2>Gruppen-Karte</h2>
            <div class="map-container">
                <canvas id="map"></canvas>
                <div class="map-controls">
                    <button onclick="zoomIn()" title="Zoom +">+</button>
                    <button onclick="zoomOut()" title="Zoom -">−</button>
                    <button onclick="resetView()" title="Ansicht zurücksetzen">⌂</button>
                </div>
                <div id="group-popup">
                    <div class="popup-header">
                        <span class="popup-title" id="popup-title">Gruppe</span>
                        <button class="popup-close" onclick="closePopup()">×</button>
                    </div>
                    <div id="popup-content"></div>
                </div>
                <div class="map-legend">
                    <span>Klicke auf eine Gruppe für Details</span>
                    <span>Mausrad = Zoom, Ziehen = Verschieben</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Verdächtige Aktivitäten <span class="count" id="suspicious-count">0</span></h2>
            <div id="suspicious-list" style="max-height: 400px; overflow-y: auto;"></div>
        </div>

        <div class="card">
            <h2>Multi-Account Verdacht <span class="count" id="multi-count">0</span></h2>
            <div id="multi-list"></div>
        </div>

        <div class="card">
            <h2>Erkannte Gruppen <span class="count ok" id="group-count">0</span></h2>
            <div id="group-list"></div>
        </div>
    </div>

    <script>
        const colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff8c32', '#a66cff', '#fc5185', '#3ec1d3'];

        let logTimeRange = { start: null, end: null };
        let currentFilter = { start: null, end: null };

        async function loadData() {
            try {
                let url = '/api/data';
                if (currentFilter.start || currentFilter.end) {
                    const params = new URLSearchParams();
                    if (currentFilter.start) params.set('start', currentFilter.start);
                    if (currentFilter.end) params.set('end', currentFilter.end);
                    url += '?' + params.toString();
                }
                const resp = await fetch(url);
                const data = await resp.json();
                logTimeRange = data.time_range;
                updateSliderLabels();
                updateSliderDisplay();
                renderData(data);
            } catch (e) {
                console.error('Fehler beim Laden:', e);
            }
        }

        function updateSliderLabels() {
            document.getElementById('log-start').textContent = logTimeRange.start_display || '--:--';
            document.getElementById('log-end').textContent = logTimeRange.end_display || '--:--';
        }

        function getTimeForPercent(percent) {
            if (!logTimeRange.start || !logTimeRange.end) return null;
            const start = new Date(logTimeRange.start);
            const end = new Date(logTimeRange.end);
            const range = end - start;
            return new Date(start.getTime() + range * percent / 100);
        }

        function formatTime(date) {
            if (!date) return '--:--';
            return date.toTimeString().substring(0, 5);
        }

        function getFilterTime(percent) {
            const time = getTimeForPercent(percent);
            if (!time) return null;
            return time.toISOString().replace('T', ' ').substring(0, 19);
        }

        function updateSliderDisplay() {
            const startPercent = parseInt(document.getElementById('slider-start').value);
            const endPercent = parseInt(document.getElementById('slider-end').value);

            const startTime = getTimeForPercent(startPercent);
            const endTime = getTimeForPercent(endPercent);

            document.getElementById('slider-start-value').textContent = formatTime(startTime);
            document.getElementById('slider-end-value').textContent = formatTime(endTime);

            // Zeige Filterinfo
            const info = document.getElementById('filter-info');
            if (startPercent > 0 || endPercent < 100) {
                info.textContent = `(Filter: ${formatTime(startTime)} - ${formatTime(endTime)})`;
            } else {
                info.textContent = '(Gesamter Zeitraum)';
            }
        }

        function applyFilter() {
            const startPercent = parseInt(document.getElementById('slider-start').value);
            const endPercent = parseInt(document.getElementById('slider-end').value);
            currentFilter.start = startPercent > 0 ? getFilterTime(startPercent) : null;
            currentFilter.end = endPercent < 100 ? getFilterTime(endPercent) : null;
            loadData();
        }

        function resetFilter() {
            document.getElementById('slider-start').value = 0;
            document.getElementById('slider-end').value = 100;
            currentFilter = { start: null, end: null };
            updateSliderDisplay();
            loadData();
        }

        function renderData(data) {
            document.getElementById('logfile').textContent = data.logfile;

            document.getElementById('stats').innerHTML = `
                <div class="stat"><div class="value">${data.stats.total_users}</div><div class="label">Spieler</div></div>
                <div class="stat"><div class="value">${data.stats.total_groups}</div><div class="label">Gruppen</div></div>
                <div class="stat ${data.stats.high_risk > 0 ? 'danger' : ''}"><div class="value">${data.stats.high_risk}</div><div class="label">Hohes Risiko</div></div>
                <div class="stat ${data.stats.medium_risk > 0 ? 'warning' : ''}"><div class="value">${data.stats.medium_risk}</div><div class="label">Mittleres Risiko</div></div>
                <div class="stat ${data.multi_accounts.length > 0 ? 'warning' : ''}"><div class="value">${data.multi_accounts.length}</div><div class="label">Multi-Accounts</div></div>
            `;

            // Multi-Accounts
            document.getElementById('multi-count').textContent = data.multi_accounts.length;
            const multiList = document.getElementById('multi-list');
            multiList.innerHTML = data.multi_accounts.length === 0
                ? '<div class="empty">Keine Multi-Accounts erkannt</div>'
                : data.multi_accounts.map(m => `
                    <div class="multi-account">
                        <div class="ip">${m.ip} <span style="color:#888">[${m.count} Accounts]</span></div>
                        <div class="users">${m.users.join(', ')}</div>
                    </div>
                `).join('');

            // Verdächtige (IP-basiert)
            document.getElementById('suspicious-count').textContent = data.suspicious.length;
            const suspList = document.getElementById('suspicious-list');
            suspList.innerHTML = data.suspicious.length === 0
                ? '<div class="empty">Keine verdächtigen Aktivitäten</div>'
                : data.suspicious.map(s => {
                    const levelText = s.level === 'high' ? 'HOCH' : (s.level === 'medium' ? 'MITTEL' : 'NIEDRIG');
                    return `
                    <div class="suspicious ${s.level}">
                        <div class="header">
                            <span class="ip-info">${s.ip}</span>
                            <span class="level">${levelText}</span>
                        </div>
                        <div class="usernames">Accounts: ${s.usernames.join(', ')}</div>
                        <div class="details">${s.user_group ? 'Gruppe ' + s.user_group : 'Keine Gruppe'}</div>
                        <div class="time-breakdown">
                            <span class="after">${s.after_count}x NACH Etablierung</span>
                            <span class="before">${s.before_count}x davor</span>
                        </div>
                        ${s.targets.map(t => `
                            <div class="target">
                                <span class="victim">Gruppe ${t.victim_group}</span>
                                (${t.victim_members.slice(0,2).join(', ')}${t.victim_members.length > 2 ? '...' : ''})
                                ${t.established_at ? `<span style="color:#666"> - etabliert ${t.established_at}</span>` : ''}
                                <br><span class="after">${t.after_count}x nach</span> / <span class="before">${t.before_count}x vor</span>
                            </div>
                        `).join('')}
                    </div>
                `}).join('');

            // Gruppen
            document.getElementById('group-count').textContent = data.groups.length;
            const groupList = document.getElementById('group-list');
            groupList.innerHTML = data.groups.length === 0
                ? '<div class="empty">Keine Gruppen erkannt</div>'
                : data.groups.map((g, i) => `
                    <div class="group-item" style="border-left-color: ${colors[i % colors.length]}">
                        <div class="name">Gruppe ${g.id}</div>
                        <div class="members">${g.members.join(', ')}</div>
                        <div class="ips">IPs: ${g.ips.join(', ')}</div>
                        <div class="info">
                            <span>${g.total_blocks} Blöcke</span>
                            ${g.established_at ? `<span>Etabliert: ${g.established_at}</span>` : ''}
                            ${g.first_activity && g.last_activity ? `<span>Aktiv: ${g.first_activity} - ${g.last_activity}</span>` : ''}
                        </div>
                    </div>
                `).join('');

            drawMap(data);
        }

        // Map state für Zoom und Pan
        let mapState = {
            zoom: 1,
            panX: 0,
            panY: 0,
            dragging: false,
            lastX: 0,
            lastY: 0,
            data: null,
            groupRects: []  // Speichert Gruppen-Positionen für Klick-Erkennung
        };

        function drawMap(data) {
            mapState.data = data;
            window.lastData = data;

            const canvas = document.getElementById('map');
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            const width = rect.width, height = rect.height;

            ctx.fillStyle = '#0d1117';
            ctx.fillRect(0, 0, width, height);

            if (!data.groups || data.groups.length === 0) {
                ctx.fillStyle = '#666';
                ctx.font = '16px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('Keine Gruppen-Daten', width/2, height/2);
                mapState.groupRects = [];
                return;
            }

            const bounds = data.bounds;
            const padding = 40;
            const mapWidth = bounds.max_x - bounds.min_x || 100;
            const mapHeight = bounds.max_z - bounds.min_z || 100;
            const baseScale = Math.min((width - padding * 2) / mapWidth, (height - padding * 2) / mapHeight);
            const scale = baseScale * mapState.zoom;

            const centerX = (bounds.min_x + bounds.max_x) / 2;
            const centerZ = (bounds.min_z + bounds.max_z) / 2;
            const offsetX = width / 2 - (centerX - bounds.min_x) * scale + mapState.panX;
            const offsetZ = height / 2 - (centerZ - bounds.min_z) * scale + mapState.panY;

            function toScreen(x, z) {
                return {
                    x: offsetX + (x - bounds.min_x) * scale,
                    y: offsetZ + (z - bounds.min_z) * scale
                };
            }

            // Grid (dynamisch angepasst an Zoom)
            ctx.strokeStyle = '#1a1a2e';
            ctx.lineWidth = 1;
            const gridStep = Math.pow(10, Math.floor(Math.log10(mapWidth / (5 * mapState.zoom))));
            for (let x = Math.floor(bounds.min_x / gridStep) * gridStep; x <= bounds.max_x; x += gridStep) {
                const p = toScreen(x, 0);
                if (p.x >= 0 && p.x <= width) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, 0);
                    ctx.lineTo(p.x, height);
                    ctx.stroke();
                }
            }
            for (let z = Math.floor(bounds.min_z / gridStep) * gridStep; z <= bounds.max_z; z += gridStep) {
                const p = toScreen(0, z);
                if (p.y >= 0 && p.y <= height) {
                    ctx.beginPath();
                    ctx.moveTo(0, p.y);
                    ctx.lineTo(width, p.y);
                    ctx.stroke();
                }
            }

            // Zuerst: Gebaute Blöcke als Punkte zeichnen (unter den Zonen)
            data.groups.forEach((group, i) => {
                const color = colors[i % colors.length];
                if (group.places && group.places.length > 0) {
                    ctx.fillStyle = color;
                    // Punktgröße abhängig vom Zoom
                    const pointSize = Math.max(1, Math.min(3, mapState.zoom));
                    group.places.forEach(place => {
                        const p = toScreen(place.x, place.z);
                        // Nur zeichnen wenn im sichtbaren Bereich
                        if (p.x >= -10 && p.x <= width + 10 && p.y >= -10 && p.y <= height + 10) {
                            ctx.fillRect(p.x - pointSize/2, p.y - pointSize/2, pointSize, pointSize);
                        }
                    });
                }
            });

            // Gruppen-Zonen zeichnen und Positionen speichern
            mapState.groupRects = [];
            data.groups.forEach((group, i) => {
                const color = colors[i % colors.length];
                const p1 = toScreen(group.zone.x1, group.zone.z1);
                const p2 = toScreen(group.zone.x2, group.zone.z2);

                const rectX = Math.min(p1.x, p2.x);
                const rectY = Math.min(p1.y, p2.y);
                const rectW = Math.abs(p2.x - p1.x);
                const rectH = Math.abs(p2.y - p1.y);

                // Speichere für Klick-Erkennung
                mapState.groupRects.push({
                    x: rectX, y: rectY, w: rectW, h: rectH,
                    group: group, color: color
                });

                // Zeichne Zone-Rahmen (ohne Füllung, damit Blöcke sichtbar bleiben)
                ctx.strokeStyle = color;
                ctx.lineWidth = 3;
                ctx.strokeRect(rectX, rectY, rectW, rectH);

                // Label nur wenn gross genug
                if (rectW > 60 && rectH > 40) {
                    const center = toScreen(group.center.x, group.center.z);
                    // Hintergrund für bessere Lesbarkeit
                    ctx.fillStyle = '#0d1117cc';
                    const labelWidth = 100;
                    const labelHeight = 30;
                    ctx.fillRect(center.x - labelWidth/2, center.y - 18, labelWidth, labelHeight);
                    ctx.fillStyle = color;
                    ctx.font = 'bold 14px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('Gruppe ' + group.id, center.x, center.y - 4);
                    ctx.font = '11px sans-serif';
                    ctx.fillStyle = '#ccc';
                    const memberText = group.members.slice(0, 3).join(', ') + (group.members.length > 3 ? '...' : '');
                    ctx.fillText(memberText, center.x, center.y + 10);
                }
            });

            // Zoom-Info anzeigen
            ctx.fillStyle = '#666';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('Zoom: ' + Math.round(mapState.zoom * 100) + '%', 10, height - 10);
        }

        // Zoom Funktionen
        function zoomIn() {
            mapState.zoom = Math.min(mapState.zoom * 1.5, 10);
            drawMap(mapState.data || {groups: [], bounds: {}});
        }

        function zoomOut() {
            mapState.zoom = Math.max(mapState.zoom / 1.5, 0.5);
            drawMap(mapState.data || {groups: [], bounds: {}});
        }

        function resetView() {
            mapState.zoom = 1;
            mapState.panX = 0;
            mapState.panY = 0;
            closePopup();
            drawMap(mapState.data || {groups: [], bounds: {}});
        }

        // Popup Funktionen
        function showGroupPopup(group, color, screenX, screenY) {
            const popup = document.getElementById('group-popup');
            const title = document.getElementById('popup-title');
            const content = document.getElementById('popup-content');

            title.innerHTML = '<span style="color:' + color + '">Gruppe ' + group.id + '</span>';
            content.innerHTML = `
                <div class="popup-row">
                    <span class="popup-label">Mitglieder</span>
                    <span class="popup-members">${group.members.join(', ')}</span>
                </div>
                <div class="popup-row">
                    <span class="popup-label">IPs</span>
                    <span class="popup-value" style="font-family:monospace;font-size:11px;">${group.ips.join(', ')}</span>
                </div>
                <div class="popup-row">
                    <span class="popup-label">Gebaute Blöcke</span>
                    <span class="popup-value">${group.total_blocks}</span>
                </div>
                <div class="popup-row">
                    <span class="popup-label">Zone</span>
                    <span class="popup-value" style="font-family:monospace;">
                        (${group.zone.x1}, ${group.zone.z1}) bis (${group.zone.x2}, ${group.zone.z2})
                    </span>
                </div>
                ${group.established_at ? `
                <div class="popup-row">
                    <span class="popup-label">Etabliert um</span>
                    <span class="popup-value">${group.established_at}</span>
                </div>` : ''}
                ${group.first_activity && group.last_activity ? `
                <div class="popup-row">
                    <span class="popup-label">Aktivität</span>
                    <span class="popup-value">${group.first_activity} - ${group.last_activity}</span>
                </div>` : ''}
            `;

            // Position berechnen
            const container = document.querySelector('.map-container');
            const containerRect = container.getBoundingClientRect();
            let popupX = screenX + 10;
            let popupY = screenY + 10;

            // Am Rand umklappen
            popup.style.display = 'block';
            if (popupX + popup.offsetWidth > containerRect.width - 10) {
                popupX = screenX - popup.offsetWidth - 10;
            }
            if (popupY + popup.offsetHeight > containerRect.height - 10) {
                popupY = screenY - popup.offsetHeight - 10;
            }

            popup.style.left = Math.max(10, popupX) + 'px';
            popup.style.top = Math.max(10, popupY) + 'px';
            popup.style.borderColor = color;
        }

        function closePopup() {
            document.getElementById('group-popup').style.display = 'none';
        }

        // Canvas Event Handler
        function setupCanvasEvents() {
            const canvas = document.getElementById('map');

            // Mausrad Zoom
            canvas.addEventListener('wheel', (e) => {
                e.preventDefault();
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const oldZoom = mapState.zoom;
                if (e.deltaY < 0) {
                    mapState.zoom = Math.min(mapState.zoom * 1.2, 10);
                } else {
                    mapState.zoom = Math.max(mapState.zoom / 1.2, 0.5);
                }

                // Zoom zum Mauszeiger
                const zoomFactor = mapState.zoom / oldZoom;
                mapState.panX = mouseX - (mouseX - mapState.panX) * zoomFactor;
                mapState.panY = mouseY - (mouseY - mapState.panY) * zoomFactor;

                drawMap(mapState.data || {groups: [], bounds: {}});
            });

            // Drag zum Verschieben
            canvas.addEventListener('mousedown', (e) => {
                mapState.dragging = true;
                mapState.lastX = e.clientX;
                mapState.lastY = e.clientY;
                canvas.style.cursor = 'grabbing';
            });

            canvas.addEventListener('mousemove', (e) => {
                if (mapState.dragging) {
                    mapState.panX += e.clientX - mapState.lastX;
                    mapState.panY += e.clientY - mapState.lastY;
                    mapState.lastX = e.clientX;
                    mapState.lastY = e.clientY;
                    drawMap(mapState.data || {groups: [], bounds: {}});
                }
            });

            canvas.addEventListener('mouseup', () => {
                mapState.dragging = false;
                canvas.style.cursor = 'grab';
            });

            canvas.addEventListener('mouseleave', () => {
                mapState.dragging = false;
                canvas.style.cursor = 'grab';
            });

            // Klick auf Gruppe
            canvas.addEventListener('click', (e) => {
                if (mapState.dragging) return;

                const rect = canvas.getBoundingClientRect();
                const x = (e.clientX - rect.left) * window.devicePixelRatio;
                const y = (e.clientY - rect.top) * window.devicePixelRatio;

                // Prüfe ob Klick in einer Gruppe
                for (const gr of mapState.groupRects) {
                    const gx = gr.x * window.devicePixelRatio;
                    const gy = gr.y * window.devicePixelRatio;
                    const gw = gr.w * window.devicePixelRatio;
                    const gh = gr.h * window.devicePixelRatio;

                    if (x >= gx && x <= gx + gw && y >= gy && y <= gy + gh) {
                        showGroupPopup(gr.group, gr.color, e.clientX - rect.left, e.clientY - rect.top);
                        return;
                    }
                }
                closePopup();
            });
        }

        loadData();
        setupCanvasEvents();
        window.addEventListener('resize', () => drawMap(mapState.data || {groups: [], bounds: {}}));
    </script>
</body>
</html>'''

    def log_message(self, format, *args):
        if '200' not in str(args):
            print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    parser = argparse.ArgumentParser(
        description="Web-Oberfläche für Grief-Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python grief_web.py logs/06.log              # Startet auf Port 8080
  python grief_web.py logs/06.log -p 9000      # Anderer Port
        """
    )
    parser.add_argument("logfile", help="Pfad zur Logdatei")
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="Port für Webserver (Default: 8080)")
    parser.add_argument("--group-radius", type=int, default=100,
                        help="Max. Distanz für Gruppen-Clustering (Default: 100)")
    parser.add_argument("--min-places", type=int, default=20,
                        help="Min. Blöcke um User einer Zone zuzuordnen (Default: 20)")
    args = parser.parse_args()

    if not os.path.exists(args.logfile):
        print(f"Fehler: Logfile '{args.logfile}' nicht gefunden!")
        sys.exit(1)

    GriefWebHandler.logfile = args.logfile
    GriefWebHandler.group_radius = args.group_radius
    GriefWebHandler.min_places = args.min_places

    server = HTTPServer(('0.0.0.0', args.port), GriefWebHandler)
    print(f"Grief Detection Web-Monitor gestartet")
    print(f"Logfile: {args.logfile}")
    print(f"URL: http://localhost:{args.port}")
    print(f"Strg+C zum Beenden")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")


if __name__ == "__main__":
    main()
