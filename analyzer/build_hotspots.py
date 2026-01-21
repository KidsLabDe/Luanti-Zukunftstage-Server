import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import sys

def main():
    # 1. Setup Input Parameters
    parser = argparse.ArgumentParser(description="Visualize player activity hotspots from server logs.")
    parser.add_argument("logfile", help="Path to the server log file")
    parser.add_argument("player", help="Name of the player to filter by")
    args = parser.parse_args()

    # 2. Regex for parsing (X, Y, Z) and Action
    # Captures Player, Action, and Coordinates
    #pattern = re.compile(r"ACTION\[Server\]: (\w+) (?:digs|places node) .* at \(([-0-9]+),([-0-9]+),([-0-9]+)\)")
    # This version captures the player, the verb/action, and the coordinates
    # regardless of what the action is.
    pattern = re.compile(r"ACTION\[Server\]: (\w+) (\S+) .* at \(([-0-9]+),([-0-9]+),([-0-9]+)\)")

    data = []

    # 3. Read and Filter Log File
    try:
        with open(args.logfile, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    p_name, action, x, y, z = match.groups()
                    # Filter for the specific player (case-insensitive)
                    if p_name.lower() == args.player.lower():
                        data.append({'x': int(x), 'z': int(z)})
    except FileNotFoundError:
        print(f"Error: File '{args.logfile}' not found.")
        sys.exit(1)

    if not data:
        print(f"No coordinate data found for player: {args.player}")
        return

    df = pd.DataFrame(data)

    # 4. Create the Hotspot Visualization
    plt.figure(figsize=(12, 10))
    
    # Use a 2D Density Plot (Hotspot)
    sns.kdeplot(
        data=df, x="x", y="z", 
        fill=True, 
        thresh=0, 
        levels=100, 
        cmap="mako"
    )

    # Overlap with individual points for precision
    plt.scatter(df['x'], df['z'], color='white', s=5, alpha=0.3, label="Exact Actions")

    plt.title(f"Activity Hotspots for Player: {args.player}", fontsize=16)
    plt.xlabel("X Coordinate")
    plt.ylabel("Z Coordinate")
    plt.grid(True, linestyle='--', alpha=0.4)
    
    # Save the output
    output_name = f"{args.player}_hotspots.png"
    plt.savefig(output_name)
    print(f"Successfully generated visualization: {output_name}")
    plt.show()

if __name__ == "__main__":
    main()
