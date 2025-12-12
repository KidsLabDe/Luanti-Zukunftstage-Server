# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Luanti/Minetest server setup for "Zukunftsnächte" (Future Nights) - educational workshops where students build their vision of future cities using real-world OpenStreetMap data. The project is run by KidsLab.de in cooperation with the Bayerische Landeszentrale für politische Bildungsarbeit.

## Common Commands

### Starting Servers

```bash
# Start workshop world interactively (prompts for world number)
./startWorkshop.sh

# Start workshop world without Docker
./startWorkshopNoDocker.sh

# Start a specific numbered world (e.g., world 05)
docker compose -f 05.yaml up

# Start in detached mode
docker compose -f 05.yaml start
```

### World Generation (world2minetest)

```bash
cd w2mt
pip3 install -r requirements.txt
python3 w2mt.py  # Main script for generating worlds from OSM data
```

## Architecture

### Docker Configuration
- Each world has its own `XX.yaml` docker-compose file (00.yaml through 19.yaml, plus 77.yaml)
- `workshop.yaml` - Dynamic workshop world (uses `$WORLDNAME` env var)
- `tutorial.yaml` - Static tutorial world (KidsLab)
- All containers use `ghcr.io/linuxserver/luanti:latest` image
- Port mapping: Each world gets a unique UDP port (30000, 30101, 30140, etc.)

### Directory Structure
- `games/` - Game modes: `antigrief` (no fire/lava), `mineclonia`, `minetest`, `devtest`
- `mods/` - Server-wide mods (worldedit, travelnet, unified_inventory, world2minetest, etc.)
- `worlds/` - World data directories
- `main-config/` - Template configs (`workshop.conf`, `tutorial.conf`)
- `w2mt/` - world2minetest tool for generating worlds from OpenStreetMap data
- `docs/` - German documentation for workshop setup and server management

### Key Configuration Files
- `minetest.conf` - Main server configuration
- `main-config/workshop.conf` - Workshop template (uses `mg_name = singlenode` for OSM worlds)
- World-specific config in `worlds/XX-CityName/world.mt`

### World Setup
- Worlds are identified by `world_name` in `world.mt`, not folder name
- Folder convention: `XX-CityName` (e.g., `05-Arnstorf`)
- `gameid = antigrief` recommended for workshops
- `backend = leveldb` for better storage
- `map.dat` from world2minetest goes into `mods/world2minetest/` (shared across all worlds)

### OSM World Generation Flow
1. Create world folder: `XX-CityName`
2. Set `world_name = XX` in `world.mt`
3. Generate `map.dat` using w2mt tools
4. Copy `map.dat` to `mods/world2minetest/`
5. Start server with corresponding yaml file

## Important Notes

- Default password for new users: see `default_password` in config files
- Admin user: `Mentor`
- Server is in creative mode with damage/PvP disabled
- Default privileges include fly, teleport, noclip for educational purposes
