import pandas as pd
import re
import plotly.express as px
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", help="Path to the Luanti log file")
    args = parser.parse_args()

    # Regex captures: Player, Action, Block Type, X, Y, Z
    pattern = re.compile(r"ACTION\[Server\]: (\w+) (digs|places node) (.*) at \(([-0-9]+),([-0-9]+),([-0-9]+)\)")
    
    data = []
    if not os.path.exists(args.logfile):
        print(f"File {args.logfile} not found.")
        return

    with open(args.logfile, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                p_name, action, block, x, y, z = match.groups()
                data.append({
                    'player': p_name, 
                    'action': action, 
                    'block': block,
                    'x': int(x), 
                    'y': int(y), 
                    'z': int(z)
                })

    if not data:
        print("No coordinate data found in the log file.")
        return

    df = pd.DataFrame(data)

    # --- 3D SCATTER MAP ---
    # We set 'color' to 'player' so everyone gets their own color automatically
    fig_3d = px.scatter_3d(
        df, x='x', y='z', z='y',
        color='player',
        symbol='action',  # Different shapes for digging vs placing
        hover_name='player',
        hover_data={'action': True, 'block': True, 'x': True, 'y': True, 'z': True},
        title="Server Activity Map: Player Comparison",
        labels={'z': 'Height (Y)', 'y': 'Z-Plane'}
    )

    # Adjusting marker size for better visibility
    fig_3d.update_traces(marker=dict(size=4, line=dict(width=0)))
    
    # Improve the 3D layout ratio
    fig_3d.update_layout(scene=dict(aspectmode='data'))

    # --- 2D TOP-DOWN MAP ---
    fig_2d = px.scatter(
        df, x="x", y="z",
        color="player",
        hover_name="player",
        hover_data=["action", "block"],
        title="Top-Down View (All Players)",
        marginal_x="histogram",
        marginal_y="histogram"
    )

    fig_3d.show()
    fig_2d.show()

if __name__ == "__main__":
    main()
