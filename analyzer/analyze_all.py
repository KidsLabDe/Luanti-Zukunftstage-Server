import pandas as pd
import re
import plotly.express as px
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", help="Path to the Luanti log file")
    args = parser.parse_args()

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
                    'x': int(x), 'y': int(y), 'z': int(z)
                })

    if not data:
        print("No coordinate data found.")
        return

    df = pd.DataFrame(data)

    # --- 3D SCATTER MAP (1:1:1 Ratio) ---
    fig_3d = px.scatter_3d(
        df, x='x', y='z', z='y',
        color='player',
        symbol='action',
        hover_name='player',
        hover_data={'action': True, 'block': True},
        title="3D Server Activity (1:1:1 Scale)",
        labels={'z': 'Height (Y)', 'y': 'Z-Plane'}
    )
    
    # aspectmode='data' ensures 1 unit on X = 1 unit on Y = 1 unit on Z
    fig_3d.update_layout(
        scene=dict(aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # --- 2D TOP-DOWN MAP (1:1 Ratio) ---
    fig_2d = px.scatter(
        df, x="x", y="z",
        color="player",
        hover_name="player",
        hover_data=["block"],
        title="Top-Down View (Fixed 1:1 Aspect Ratio)"
    )

    # scaleanchor ensures that X and Z axes scale equally
    fig_2d.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    fig_3d.show()
    fig_2d.show()

if __name__ == "__main__":
    main()
