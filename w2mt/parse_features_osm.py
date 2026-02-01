import argparse
import json
import sys
from collections import defaultdict

from pyproj import CRS, Transformer

from _util import SURFACES, DECORATIONS, is_area_relation, is_building_relation


def status(message, end="\n"):
    """Print status message with flush for immediate display"""
    print(f"   {message}", end=end, flush=True)


# Coordinate transformer (can be at module level)
transform_coords = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(25832)).transform


def get_nodepos(lat, lon):
    x, y = transform_coords(lat, lon)
    return int(round(x)), int(round(y))


def print_element(msg, e):
    print(msg, f"{e.get('id', 0)} {e.get('type', 'undefined')}[{','.join(k+'='+v for k,v in e.get('tags', {}).items())}]")


def get_surface(area):
    tags = area["tags"]
    surface = None
    res_area = None

    if "surface" in tags and tags["surface"] in SURFACES:
        if tags["surface"] in ["natural", "building_ground"]:
            return tags["surface"], "low"
        elif tags["surface"] in ["residential_landuse", "landuse", "leisure", "sports_centre", "pitch", "amenity", "school"]:
            return tags["surface"], "medium"
        elif tags["surface"] in ["grass", "asphalt", "paving_stones", "fine_gravel", "concrete", "dirt", "highway", "footway", "cycleway", "pedestrian", "path", "park", "playground", "parking", "village_green", "water"]:
            return tags["surface"], "high"
        else:
            return tags["surface"], "low"

    if "natural" in tags:
        if tags["natural"] == "water":
            return "water", "medium"
        else:
            return "natural", "low"
    elif "amenity" in tags:
        if tags["amenity"] in SURFACES:
            return tags["amenity"], "medium"
        elif tags["amenity"] == "grave_yard":
            return "village_green", "medium"
        else:
            surface = "amenity"
            res_area = "medium"
    elif "leisure" in tags:
        if tags["leisure"] in SURFACES:
            return tags["leisure"], "medium"
        elif tags["leisure"] == "swimming_pool":
            return "water", "high"
        else:
            surface = "leisure"
            res_area = "high"
    elif "landuse" in tags:
        if tags["landuse"] == "residential":
            return "residential_landuse", "low"
        elif tags["landuse"] == "reservoir":
            return "water", "low"
        elif tags["landuse"] == "grass" or tags["landuse"] == "meadow" or tags["landuse"] == "forest":
            return "natural", "medium"
        elif tags["landuse"] in SURFACES:
            return tags["landuse"], "low"
        else:
            surface = "landuse"
            res_area = "low"
    elif "place" in tags:
        if tags["place"] == "islet":
            return "default", "low"
    return surface, "low"


def building_height(tags):
    try:
        levels = int(tags["building:levels"])
    except (KeyError, ValueError):
        levels = 0

    try:
        roof_levels = int(tags["roof:levels"])
    except (KeyError, ValueError):
        roof_levels = 0

    levels += roof_levels
    if levels > 0:
        return 3 * levels

    if "building" in tags:
        if tags["building"] in ["yes", "bungalow", "toilets"]:
            return 3
        elif tags["building"] in ["school", "college", "train_station", "transportation", "barn"]:
            return 6
        elif tags["building"] in ["hospital", "university", "barn"]:
            return 9
        elif tags["building"] in ["church", "mosque", "synagogue", "temple", "government"]:
            return 12
        elif tags["building"] in ["cathedral"]:
            return 15
    if "tower:type" in tags:
        if tags["tower:type"] in ["bell_tower"]:
            return 27
    return 2


def node_ids_to_node_positions(node_ids, node_id_to_blockpos_local):
    x_coords = []
    y_coords = []
    for node_id in node_ids:
        if node_id not in node_id_to_blockpos_local:
            continue
        pos = node_id_to_blockpos_local.get(node_id)
        if pos:
            x, y = pos
            x_coords.append(x)
            y_coords.append(y)
    return x_coords, y_coords


# Processing functions for multiprocessing
def process_outer_areas(outer_areas_list, node_id_to_blockpos_local):
    res = {"outer": []}
    min_x, max_x, min_y, max_y = None, None, None, None
    for area in outer_areas_list:
        surface, level = get_surface(area)
        level = "outer"
        if surface is None:
            continue
        x_coords, y_coords = node_ids_to_node_positions(area["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res[level].append({"x": x_coords, "y": y_coords, "surface": surface, "osm_id": area["id"]})
    return {"areas": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_inner_empty_areas(inner_empty_areas_list, node_id_to_blockpos_local):
    res = {"inner": []}
    min_x, max_x, min_y, max_y = None, None, None, None
    for hole in inner_empty_areas_list:
        surface = "default"
        level = "inner"
        try:
            myNodes = hole["nodes"]
        except:
            continue
        x_coords, y_coords = node_ids_to_node_positions(hole["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res[level].append({"x": x_coords, "y": y_coords, "surface": surface, "osm_id": hole["id"]})
    return {"areas": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_areas(areas_list, node_id_to_blockpos_local):
    res = {"low": [], "medium": [], "high": []}
    min_x, max_x, min_y, max_y = None, None, None, None
    for area in areas_list:
        surface, level = get_surface(area)
        if surface is None:
            continue
        x_coords, y_coords = node_ids_to_node_positions(area["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res[level].append({"x": x_coords, "y": y_coords, "surface": surface, "osm_id": area["id"]})
    return {"areas": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_buildings(buildings_list, node_id_to_blockpos_local):
    res = []
    min_x, max_x, min_y, max_y = None, None, None, None
    for building in buildings_list:
        x_coords, y_coords = node_ids_to_node_positions(building["nodes"], node_id_to_blockpos_local)
        if len(x_coords) < 2:
            continue
        tags = building["tags"]
        material = None
        if "building:material" in tags and tags["building:material"] == "brick":
            material = "brick"
        is_building_part = "building:part" in tags
        b = {"x": x_coords, "y": y_coords, "is_part": is_building_part, "osm_id": building.get("id")}
        try:
            height = int(tags["building:height"].split(' m')[0])
        except:
            height = building_height(tags)
        else:
            height = min(height, 255)
        b["height"] = height
        if material is not None:
            b["material"] = material
        res.append(b)
    return {"buildings": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_barriers(barriers_list, node_id_to_blockpos_local):
    res = defaultdict(list)
    min_x, max_x, min_y, max_y = None, None, None, None
    for barrier in barriers_list:
        deco = barrier["tags"].get("barrier")
        if deco not in DECORATIONS:
            deco = "barrier"
        x_coords, y_coords = node_ids_to_node_positions(barrier["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res[deco].append({"x": x_coords, "y": y_coords})
    return {"decorations": dict(res), "min_max": (min_x, max_x, min_y, max_y)}


def process_waterways(waterways_list, node_id_to_blockpos_local):
    res = []
    min_x, max_x, min_y, max_y = None, None, None, None
    for waterway in waterways_list:
        tags = waterway["tags"]
        surface = "water" if "waterway" in tags else None
        layer = tags.get("layer", 0)
        try:
            layer = int(layer)
        except ValueError:
            layer = 0
        x_coords, y_coords = node_ids_to_node_positions(waterway["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res.append({"x": x_coords, "y": y_coords, "surface": surface, "layer": layer, "osm_id": waterway["id"], "type": tags["waterway"]})
    return {"waterways": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_highways(highways_list, node_id_to_blockpos_local):
    res = []
    min_x, max_x, min_y, max_y = None, None, None, None
    for highway in highways_list:
        tags = highway["tags"]
        surface = tags.get("highway") if tags.get("highway") in SURFACES else tags.get("surface") if "surface" in tags and tags.get("surface") in SURFACES else "highway"
        layer = tags.get("layer", 0)
        try:
            layer = int(layer)
        except ValueError:
            layer = 0
        if "tunnel" in tags and tags["tunnel"] != "building_passage":
            layer = -1 if "layer" not in tags else min(0, int(tags.get("layer", -1)))
        x_coords, y_coords = node_ids_to_node_positions(highway["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res.append({"x": x_coords, "y": y_coords, "surface": surface, "layer": layer, "osm_id": highway["id"], "type": tags["highway"]})
    return {"highways": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_railways(railways_list, node_id_to_blockpos_local):
    res = []
    min_x, max_x, min_y, max_y = None, None, None, None
    for railway in railways_list:
        tags = railway["tags"]
        railway_type = tags.get("railway", "rail")
        surface = railway_type if railway_type in SURFACES else "railway"
        layer = tags.get("layer", 0)
        try:
            layer = int(layer)
        except ValueError:
            layer = 0
        if "tunnel" in tags:
            layer = -1 if "layer" not in tags else min(0, int(tags.get("layer", -1)))
        x_coords, y_coords = node_ids_to_node_positions(railway["nodes"], node_id_to_blockpos_local)
        if x_coords:
            min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
            max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
            min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
            max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)
            res.append({"x": x_coords, "y": y_coords, "surface": surface, "layer": layer, "osm_id": railway["id"], "type": railway_type})
    return {"railways": res, "min_max": (min_x, max_x, min_y, max_y)}


def process_nodes(nodes_list, node_id_to_blockpos_local):
    res = defaultdict(list)
    min_x, max_x, min_y, max_y = None, None, None, None
    for node in nodes_list:
        tags = node["tags"]
        deco = None
        if "natural" in tags and tags["natural"] in DECORATIONS:
            deco = tags["natural"]
        elif "amenity" in tags and tags["amenity"] in DECORATIONS:
            deco = tags["amenity"]
        elif "barrier" in tags:
            deco = tags["barrier"] if tags["barrier"] in DECORATIONS else "barrier"
        if not deco:
            continue
        x, y = get_nodepos(node["lat"], node["lon"])
        min_x = x if min_x is None else min(min_x, x)
        max_x = x if max_x is None else max(max_x, x)
        min_y = y if min_y is None else min(min_y, y)
        max_y = y if max_y is None else max(max_y, y)
        res[deco].append({"x": x, "y": y})
    return {"decorations": dict(res), "min_max": (min_x, max_x, min_y, max_y)}


def main():
    parser = argparse.ArgumentParser(description="Parse OSM data")
    parser.add_argument("file", type=argparse.FileType("r", encoding="utf-8"), help="GeoJSON file with OSM data")
    parser.add_argument("--output", "-o", type=argparse.FileType("w"), help="Output file", default="./parsed_data/features_osm.json")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Load data
    data = json.load(args.file)

    # Build node_id_to_blockpos mapping
    node_id_to_blockpos = {}

    # Data structures
    outer_areas = []
    inner_empty_areas = []
    areas = []
    highways = []
    railways = []
    waterways = []
    buildings = []
    barriers = []
    nodes = []

    # Helper to find elements (needed for relations)
    def find_element(id):
        for e in data["elements"]:
            try:
                if e["id"] == id:
                    return e
            except:
                continue
        return f"no element with id {id} found"

    def rel_has_only_outer_ways(relation):
        for member in relation["members"]:
            if member["type"] != "way":
                return False
            try:
                role = member["role"]
            except:
                return False
            if role == "inner":
                return False
        return True

    def split_relation_in_areas_and_holes(relation, list_for_outer_areas, list_for_inner_areas, list_of_areas):
        areaNr = 0
        areaNodes = []
        for member in relation["members"]:
            try:
                role = member["role"]
            except:
                continue

            if member["type"] == "way":
                if rel_has_only_outer_ways(relation):
                    area_collection = list_of_areas
                elif role == "inner":
                    if is_area_relation(member):
                        continue
                    else:
                        area_collection = list_for_inner_areas
                else:
                    area_collection = list_for_outer_areas

                way = find_element(member.get('ref'))
                try:
                    myNodes = way['nodes'].copy()
                except:
                    continue

                nodesCount = len(myNodes)
                if len(areaNodes) == 0:
                    areaNodes = myNodes
                elif myNodes[-1] == areaNodes[0]:
                    myNodes.pop(-1)
                    myNodes.extend(areaNodes)
                    areaNodes = myNodes
                elif areaNodes[0] == myNodes[0]:
                    reverseNodes = myNodes[len(myNodes):0:-1]
                    reverseNodes.extend(areaNodes)
                    areaNodes = reverseNodes
                elif areaNodes[-1] == myNodes[0]:
                    areaNodes.pop(-1)
                    areaNodes.extend(myNodes)
                elif areaNodes[-1] == myNodes[-1]:
                    reverseNodes = myNodes[len(myNodes)-1::-1]
                    areaNodes.extend(reverseNodes)

                if role == "outer":
                    areaTags = relation["tags"]
                else:
                    areaTags = {"empty_area": "yes"}

                if areaNodes and areaNodes[0] == areaNodes[-1]:
                    area_collection.append({
                        "id": f"{relation['id']}.{role}#{areaNr}",
                        "nodes": areaNodes,
                        "tags": areaTags,
                    })
                    areaNodes = []
                    areaNr += 1

    # Parse elements
    total_elements = len(data["elements"])
    status(f"Verarbeite {total_elements:,} OSM-Elemente...")

    element_count = 0
    for e in data["elements"]:
        element_count += 1
        if element_count % 10000 == 0:
            status(f"   Elemente: {element_count:,}/{total_elements:,}", end="\r")

        t = e["type"]
        tags = e.get("tags")

        if tags and "boundary" in tags.keys():
            continue

        if t == "node":
            blockpos = get_nodepos(e["lat"], e["lon"])
            node_id_to_blockpos[e["id"]] = blockpos
            if tags and ("natural" in tags or "amenity" in tags or "barrier" in tags):
                nodes.append(e)
        elif t == "relation" or t == "multipolygon":
            if not tags:
                continue
            members = e.get("members")
            if not members:
                continue
            if is_area_relation(e):
                split_relation_in_areas_and_holes(e, outer_areas, inner_empty_areas, areas)
            elif is_building_relation(e):
                split_relation_in_areas_and_holes(e, buildings, buildings, buildings)
        elif t == "way":
            if not tags:
                continue
            elif "area" in tags:
                areas.append(e)
            elif "highway" in tags:
                highways.append(e)
            elif "railway" in tags:
                if tags["railway"] in {"rail", "tram", "subway", "light_rail", "narrow_gauge"}:
                    railways.append(e)
            elif "waterway" in tags:
                if tags['waterway'] in {"ditch", "drain", "stream"}:
                    waterways.append(e)
            elif "building" in tags or "building:part" in tags:
                buildings.append(e)
            elif "barrier" in tags:
                barriers.append(e)
            else:
                areas.append(e)

    status(f"✅ Elemente sortiert: {len(areas)} Flächen, {len(highways)} Straßen, {len(railways)} Schienen, {len(buildings)} Gebäude")

    # Process features (sequential - avoid multiprocessing issues)
    status("Verarbeite Features...")

    final_results = {
        "areas": {"outer": [], "inner": [], "low": [], "medium": [], "high": []},
        "buildings": [],
        "decorations": defaultdict(list),
        "highways": [],
        "railways": [],
        "waterways": []
    }
    all_min_max = []

    # Process each type sequentially
    tasks = [
        ("Flächen (outer)", process_outer_areas, outer_areas),
        ("Flächen (inner)", process_inner_empty_areas, inner_empty_areas),
        ("Flächen", process_areas, areas),
        ("Gebäude", process_buildings, buildings),
        ("Barrieren", process_barriers, barriers),
        ("Gewässer", process_waterways, waterways),
        ("Straßen", process_highways, highways),
        ("Schienen", process_railways, railways),
        ("Nodes", process_nodes, nodes),
    ]

    for name, func, data_list in tasks:
        if data_list:
            status(f"   {name}...", end="\r")
            res_dict = func(data_list, node_id_to_blockpos)
            for key, value in res_dict.items():
                if key == "min_max":
                    if value[0] is not None:
                        all_min_max.append(value)
                elif key == "areas":
                    for area_key, area_value in value.items():
                        final_results[key][area_key].extend(area_value)
                elif key == "decorations":
                    for deco_key, deco_value in value.items():
                        final_results[key][deco_key].extend(deco_value)
                else:
                    final_results[key].extend(value)

    if not all_min_max:
        status("❌ Keine Features gefunden!")
        return

    min_x = min(m[0] for m in all_min_max)
    max_x = max(m[1] for m in all_min_max)
    min_y = min(m[2] for m in all_min_max)
    max_y = max(m[3] for m in all_min_max)

    size_x = max_x - min_x + 1
    size_y = max_y - min_y + 1
    status(f"✅ Features extrahiert: {size_x}x{size_y} Blöcke")

    # Write output
    json.dump({
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "areas": final_results["areas"],
        "buildings": final_results["buildings"],
        "decorations": dict(final_results["decorations"]),
        "highways": final_results["highways"],
        "railways": final_results["railways"],
        "waterways": final_results["waterways"]
    }, args.output, indent=2)

    status(f"✅ Ausgabe geschrieben: {args.output.name}")


if __name__ == '__main__':
    main()
