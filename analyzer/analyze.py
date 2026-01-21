import pandas as pd
import re
import plotly.express as px
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile")
    parser.add_argument("player")
    args = parser.parse_args()

    # Regex for Luanti logs
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
                if p_name.lower() == args.player.lower():
                    data.append({'x': int(x), 'y': int(y), 'z': int(z), 'action': action, 'block': block})

    if not data:
        print(f"No data for {args.player}.")
        return

    df = pd.DataFrame(data)

    # --- FIGURE 1: 3D SCATTER (The Architecture) ---
    # This is usually the most helpful for Luanti/Minetest
    fig_3d = px.scatter_3d(
        df, x='x', y='z', z='y',
        color='action',
        hover_data=['block'],
        title=f"3D Build/Dig Trace: {args.player}",
        color_discrete_map={'digs': '#EF553B', 'places node': '#00CC96'}
    )
    fig_3d.update_traces(marker=dict(size=3))

    # --- FIGURE 2: 2D DENSITY (The Hotspots) ---
    # Using density_contour + scatter to avoid the marginal color error
    fig_2d = px.density_contour(
        df, x="x", y="z", 
        title=f"Activity Density: {args.player}",
        marginal_x="histogram", 
        marginal_y="histogram"
    )
    fig_2d.add_trace(px.scatter(df, x="x", y="z", color="action").data[0])

    # Display
    fig_3d.show()
    fig_2d.show()

if __name__ == "__main__":
    main()
