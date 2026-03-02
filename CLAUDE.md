# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Luanti/Minetest server setup for "Zukunftsnächte" (Future Nights) - educational workshops where students build their vision of future cities using real-world OpenStreetMap data. The project is run by KidsLab.de in cooperation with the Bayerische Landeszentrale für politische Bildungsarbeit.

## Common Commands

### Starting Servers

```bash
# Start a world interactively (prompts for world selection)
./startWorld.sh

# Start a specific world with port
./startWorld.sh 02-koeln 30102

# Stop a world
./stopWorld.sh 02-koeln
```

### World Generation (w2mt)

```bash
# Interactive world generation (prompts for name and coordinates)
./generate_world.sh

# Direct command with parameters
cd w2mt
python3 w2mt.py -p "02-Muenchen" -a "48.12,11.54,48.14,11.58" -g "mineclonia" -b "leveldb"
```

The w2mt pipeline:
1. `w2mt.py` - Main orchestrator: downloads OSM data, coordinates processing
2. `parse_features_osm.py` - Extracts features (roads, buildings, areas) from OSM JSON
3. `generate_map.py` - Converts features to `map.dat` binary format
4. `_util.py` - Defines SURFACES and DECORATIONS mappings (IDs and colors)

### Docker Image

```bash
# Build Docker image locally
./build-docker.sh

# Image is also built automatically via GitHub Actions on push to main
```

## Architecture

### Docker Configuration
- `docker-compose.yaml` - Main compose file using pre-built Docker image from GHCR
- `Dockerfile` - Builds server image with mods, games and config baked in
- All containers use `ghcr.io/kidslabde/luanti-zukunftstage-server:latest` image
- Worlds are mounted as volumes at runtime

### Directory Structure
- `server/games/` - Game modes: `antigrief` (modified minetest), `mineclonia`, `minetest`, `devtest`
- `server/mods/` - Server-wide mods including `world2minetest` (the map loader mod)
- `server/config/` - Template configs (`workshop.conf` with anti-grief settings)
- `client/` - Luanti client settings (minetest.conf for students)
- `worlds/` - World data in format `XX-CityName/` (e.g., `02-koeln/`)
- `w2mt/` - Python tools for generating worlds from OpenStreetMap data
- `analyzer/` - Grief-Analyzer web tool
- `docs/` - Workshop documentation & guides

### Key Configuration
- `server/config/workshop.conf` - Workshop settings with anti-grief protections:
  - `mg_name = singlenode` - Required for OSM worlds (disables terrain generation)
  - `enable_damage = false`, `enable_pvp = false`
  - `kidslab_no_mobs`, `kidslab_no_lava`, `kidslab_no_pistons` flags
- World-specific config in `worlds/XX-CityName/world.mt`:
  - `world_name = XX` - Must match first 2 chars of folder name
  - `gameid = mineclonia` - Game to use
  - `load_mod_world2minetest = true` - Required for OSM maps

### How startWorld.sh Works
1. Lists available worlds in `worlds/`
2. User selects world (e.g., `02-koeln`)
3. Starts Docker container with `docker-compose.yaml`, mounting the selected world

### Block Mapping (w2mt → Mineclonia)
The `server/mods/world2minetest/init.lua` maps surface IDs from `_util.py` to Mineclonia blocks:
- Roads: `mcl_colorblocks:concrete_grey` (asphalt), `mcl_core:stonebrick` (paving)
- Nature: `mcl_core:dirt_with_grass`, `mcl_core:water_source`
- Buildings: `mcl_core:sandstonesmooth2` (walls), `mcl_core:brick_block` (roof)

## Important Notes

- Default password: `zukunft` (see `server/config/workshop.conf`)
- Admin user: `Mentor`
- Coordinates format for w2mt: `lat,lon` (e.g., `48.12,11.54` for Munich)
- Generated worlds go to `worlds/<project>/world2minetest/map.dat`
- `generate_world.sh` sets `MINETEST_GAME_PATH` to `server/` and `MINETEST_WORLDS_PATH` to `worlds/`
