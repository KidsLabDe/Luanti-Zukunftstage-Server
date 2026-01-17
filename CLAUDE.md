# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Luanti/Minetest server setup for "Zukunftsnächte" (Future Nights) - educational workshops where students build their vision of future cities using real-world OpenStreetMap data. The project is run by KidsLab.de in cooperation with the Bayerische Landeszentrale für politische Bildungsarbeit.

## Common Commands

### Starting Servers

```bash
# Start workshop world interactively (prompts for world number)
./startWorkshop.sh

# Start a specific numbered world (e.g., world 01)
docker compose -f 01.yaml up

# Start in detached mode
docker compose -f 01.yaml up -d
```

### World Generation (w2mt)

```bash
cd w2mt
pip3 install -r requirements.txt

# Interactive world generation (prompts for name and coordinates)
./generate_world.sh

# Direct command with parameters
python3 w2mt.py -p "02-Muenchen" -a "48.12,11.54,48.14,11.58" -g "mineclonia" -b "leveldb"
```

The w2mt pipeline:
1. `w2mt.py` - Main orchestrator: downloads OSM data, coordinates processing
2. `parse_features_osm.py` - Extracts features (roads, buildings, areas) from OSM JSON
3. `generate_map.py` - Converts features to `map.dat` binary format
4. `_util.py` - Defines SURFACES and DECORATIONS mappings (IDs and colors)

## Architecture

### Docker Configuration
- Each world has its own `XX.yaml` docker-compose file (00.yaml through 19.yaml, plus 77.yaml)
- `workshop.yaml` - Dynamic workshop world (uses `$WORLDNAME` env var, port 30000)
- `tutorial.yaml` - Static tutorial world
- All containers use `ghcr.io/linuxserver/luanti:latest` image
- Port pattern: world 01 = port 30101, world 02 = port 30102, etc.

### Directory Structure
- `games/` - Game modes: `antigrief` (modified minetest), `mineclonia`, `minetest`, `devtest`
- `mods/` - Server-wide mods including `world2minetest` (the map loader mod)
- `worlds/` - World data in format `XX-CityName/` (e.g., `02-koeln/`)
- `main-config/` - Template configs (`workshop.conf` with anti-grief settings)
- `w2mt/` - Python tools for generating worlds from OpenStreetMap data

### Key Configuration
- `main-config/workshop.conf` - Workshop settings with anti-grief protections:
  - `mg_name = singlenode` - Required for OSM worlds (disables terrain generation)
  - `enable_damage = false`, `enable_pvp = false`
  - `kidslab_no_mobs`, `kidslab_no_lava`, `kidslab_no_pistons` flags
- World-specific config in `worlds/XX-CityName/world.mt`:
  - `world_name = XX` - Must match first 2 chars of folder name
  - `gameid = mineclonia` - Game to use
  - `load_mod_world2minetest = true` - Required for OSM maps

### How startWorkshop.sh Works
1. Lists available worlds in `worlds/`
2. User selects world number (e.g., `02`)
3. Copies `worlds/02*/world2minetest/map.dat` to `mods/world2minetest/map.dat`
4. Starts Docker with `workshop.yaml`

### Block Mapping (w2mt → Mineclonia)
The `mods/world2minetest/init.lua` maps surface IDs from `_util.py` to Mineclonia blocks:
- Roads: `mcl_colorblocks:concrete_grey` (asphalt), `mcl_core:stonebrick` (paving)
- Nature: `mcl_core:dirt_with_grass`, `mcl_core:water_source`
- Buildings: `mcl_core:sandstonesmooth2` (walls), `mcl_core:brick_block` (roof)

## Important Notes

- Default password: `zukunft` (see `main-config/workshop.conf`)
- Admin user: `Mentor`
- Coordinates format for w2mt: `lat,lon` (e.g., `48.12,11.54` for Munich)
- Generated worlds go to `worlds/<project>/world2minetest/map.dat`
