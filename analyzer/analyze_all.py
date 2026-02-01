import pandas as pd
import re
import plotly.express as px
import argparse
import os

def parse_groups(group_string):
    """Wandelt den String 'p1,p2-p3,p4' in ein Mapping-Dictionary um (Case-Insensitive)."""
    if not group_string:
        return {}
    
    mapping = {}
    groups = group_string.split('-')
    for i, group_content in enumerate(groups):
        player_names = group_content.split(',')
        group_label = f"Gruppe {i+1}"
        for name in player_names:
            # Wir speichern den Namen in Kleinbuchstaben
            mapping[name.strip().lower()] = group_label
    return mapping

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", help="Pfad zur Luanti/Minetest Logdatei")
    parser.add_argument("--groups", help="Gruppen-Definition (Format: name1,name2-name3,name4)", default="")
    args = parser.parse_args()

    group_mapping = parse_groups(args.groups)

    # Regex für Luanti/Minetest Logs
    pattern = re.compile(r"ACTION\[Server\]: (\w+) (digs|places node) (.*) at \(([-0-9]+),([-0-9]+),([-0-9]+)\)")
    
    data = []
    if not os.path.exists(args.logfile):
        print(f"Datei {args.logfile} nicht gefunden.")
        return

    with open(args.logfile, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                p_name, action, block, x, y, z = match.groups()
                
                # Case-Insensitive Check: Wir suchen mit dem kleingeschriebenen Namen
                group = group_mapping.get(p_name.lower(), "Andere")
                
                data.append({
                    'player': p_name, # Originalname für die Anzeige
                    'group': group,
                    'action': action, 
                    'block': block,
                    'x': int(x), 'y': int(y), 'z': int(z)
                })

    if not data:
        print("Keine relevanten Daten im Log gefunden.")
        return

    df = pd.DataFrame(data)

    # --- 3D SCATTER MAP ---
    fig_3d = px.scatter_3d(
        df, x='x', y='z', z='y',
        color='group',
        symbol='action',
        hover_name='player', 
        hover_data={'group': True, 'action': True, 'block': True},
        title="3D Server Aktivität (nach Gruppen gruppiert)",
        labels={'z': 'Höhe (Y)', 'y': 'Z-Ebene'}
    )
    
    fig_3d.update_layout(
        scene=dict(aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # --- 2D TOP-DOWN MAP ---
    fig_2d = px.scatter(
        df, x="x", y="z",
        color="group",
        hover_name="player",
        hover_data=["block", "action"],
        title="Top-Down Ansicht (Case-Insensitive Gruppen)"
    )

    fig_2d.update_yaxes(scaleanchor="x", scaleratio=1)

    #fig_3d.show()
    fig_2d.show()

if __name__ == "__main__":
    main()
