import argparse
import json
from collections import defaultdict

from pyproj import CRS, Transformer

from _util import SURFACES, DECORATIONS

import sys


parser = argparse.ArgumentParser(description="Parse OSM data")
parser.add_argument("file", type=argparse.FileType("r", encoding="utf-8"), help="GeoJSON file with OSM data")
parser.add_argument("--output", "-o", type=argparse.FileType("w"), help="Output file. Defaults to parsed_data/features_osm.json", default="./parsed_data/features_osm.json")

args = parser.parse_args()

# TODO OPTIMIZE: create (once) and use (often) hashmap! Check for doubles during creation. 
# Maybe we can even optimize the osm.json data export by smarter use of the query language.
def find_element(id):
    for e in data["elements"]:
        try:
            if e["id"] == id:
                return e
        except:
            continue
    return f"no element with id {id} found"


def print_element(msg, e):
    print(msg, f"{e.get('id', 0)} {e.get('type', 'undefined')}[{','.join(k+'='+v for k,v in e.get('tags', {}).items())}]")


transform_coords = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(25832)).transform
def get_nodepos(lat, lon):
    x, y = transform_coords(lat, lon)
    return int(round(x)), int(round(y))


node_id_to_blockpos = {}

def node_ids_to_node_positions(node_ids):
    x_coords = []
    y_coords = []
    for node_id in node_ids:
        if node_id not in node_id_to_blockpos:
            continue
        x, y = node_id_to_blockpos[node_id]
        x_coords.append(x)
        y_coords.append(y)
    return x_coords, y_coords


data = json.load(args.file)

min_x = None
max_x = None
min_y = None
max_y = None

def update_min_max(x_coords, y_coords):
    global min_x, max_x, min_y, max_y
    min_x = min(x_coords) if min_x is None else min(min_x, *x_coords)
    max_x = max(x_coords) if max_x is None else max(max_x, *x_coords)
    min_y = min(y_coords) if min_y is None else min(min_y, *y_coords)
    max_y = max(y_coords) if max_y is None else max(max_y, *y_coords)

def get_surface(area):
    tags = area["tags"]
    # print_element("processing area:", area)
    surface = None
    res_area = None

    # SURFACE tag given and usable, hence we use it:
    if "surface" in tags and tags["surface"] in SURFACES:
        if tags["surface"] in ["natural", "building_ground"] :
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
            # not returned yet: might be overriden by better match...
    elif "leisure" in tags:
        if tags["leisure"] in SURFACES:
            return tags["leisure"], "medium"
        elif tags["leisure"] == "swimming_pool":
            return "water", "high"
        else:
            surface = "leisure"
            res_area = "high"
            # not returned yet: might be overriden by better match...
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
            # not returned yet: might be overriden by better match...
    elif "place" in tags:
        if tags["place"] == "islet":
            return "default", "low"
    return surface, "low"

def building_height(tags):
    # is only called when there was no "height" tag.
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

    # we have no levels, since we guess height by type of building:

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
                if member['ref'] == 59683400:
                    sys.stderr.write("INNER 59683400 used as AREA.")
            elif role == "inner":
                if is_area_relation(member):
                    if member['ref'] == 59683400:
                        sys.stderr.write("INNER 59683400 LEFT OUT.")
                    continue # leave inner areas out when they are areas in their own right: they will be taken care of later
                else:
                    area_collection = list_for_inner_areas # an inner empty area
                    if member['ref'] == 59683400:
                        sys.stderr.write("INNER 59683400 used as INNER.")
            else: 
                area_collection = list_for_outer_areas
                if member['ref'] == 59683400:
                    sys.stderr.write("INNER 59683400 used as OUTER.")

            way = find_element(member.get('ref'))
            try:
                myNodes = way['nodes'].copy()
            except:
                continue

            nodesCount = len(myNodes)
            if len(areaNodes) == 0:
                print(f"xxx #0 Start ({nodesCount})")
                areaNodes = myNodes
            elif myNodes[-1] == areaNodes[0]: 
                # new way should sit in front of collected area
                myNodes.pop(-1)
                myNodes.extend(areaNodes)
                areaNodes = myNodes
                print(f"xxx #1 Prepend ({nodesCount} => {len(areaNodes)})")
            elif areaNodes[0] == myNodes[0]: 
                # new way has same head as collected area, hence we reverse it and prepend it
                reverseNodes = myNodes[len(myNodes):0:-1] # gets all but the first in reverse order
                reverseNodes.extend(areaNodes)
                areaNodes = reverseNodes
                print(f"xxx #2 Prepend reversed ({nodesCount}) => {len(areaNodes)}")
            elif areaNodes[-1] == myNodes[0]:
                # new way joins after collected area
                areaNodes.pop(-1)
                areaNodes.extend(myNodes)
                print(f"xxx #3 Extend ({nodesCount}) => {len(areaNodes)}")
            elif areaNodes[-1] == myNodes[-1]:
                # new way has same tail as collected area, hence we reverse it and extend it at end
                reverseNodes = myNodes[len(myNodes)-1::-1] # gets all but the last in reverse order
                areaNodes.extend(reverseNodes)
                print(f"xxx #4 Extend reversed ({nodesCount}) => {len(areaNodes)}")
            else:
                print(f"xxx WARNING: way {way['id']} does not fit in relation {relation['id']}, hence we ignore it.")

            # check if area is complete, i.e. path of nodes is closed:
            if role == "outer":
                areaTags = relation["tags"]
            else: 
                areaTags = { "empty_area" : "yes", }
            if areaNodes[0] == areaNodes[-1]:
                area_collection.append({
                    "id": f"{relation['id']}.{role}#{areaNr}",
                    "nodes": areaNodes,
                    "tags": areaTags,
                })
                print(f"xxx Relation {relation['id']}.{role}#{areaNr} COMPLETE and added to our areas with #{len(areaNodes)} nodes")
                areaNodes = []
                areaNr += 1
            else:
                print(f"xxx Relation {relation['id']} has #{len(areaNodes)} nodes but is still incomplete, hence we keep collecting parts ...")

    return



###################################################### START ACTION: #########################

outer_areas = []
inner_empty_areas = [] # aka holes
areas = [] # normal areas made up from ways
highways = []
waterways = []
buildings = []
barriers = []
nodes = []

from _util import is_area_relation, is_building_relation

# sort elements by type (highway, building, area or node)
for e in data["elements"]:
    t = e["type"]
    tags = e.get("tags")
    if tags and "boundary" in tags.keys():
        continue # ignore boundaries
    if t == "node":
        blockpos = get_nodepos(e["lat"], e["lon"])
        node_id_to_blockpos[e["id"]] = blockpos
        if tags and ("natural" in tags or "amenity" in tags or "barrier" in tags):
            nodes.append(e)
            continue
    elif t == "relation" or t == "multipolygon":
        if not tags:
            print_element(f"Ignored relation {e.get('id')}, missing tags:", e)
            continue
        members = e.get("members")
        if not members:
            print_element(f"Ignored relation {e.get('id')}, missing members:", e)
            continue
        if is_area_relation(e):
            print(f"Area from relation added. ID: {e.get('id')}")
            split_relation_in_areas_and_holes(e, outer_areas, inner_empty_areas, areas)
            continue
        elif is_building_relation(e):
            print(f"Building from relation added. ID: {e.get('id')}")
            split_relation_in_areas_and_holes(e, buildings, buildings, buildings)
            continue
    elif t == "way":
        if not tags:
            print_element("Ignored, missing tags:", e)
            continue
        elif "area" in tags:
            areas.append(e)
            continue
        elif "highway" in tags:
            highways.append(e)
            continue
        elif "waterway" in tags:
            if tags['waterway'] in { "ditch", "drain", "stream"}:
                waterways.append(e)
            continue
        elif "building" in tags or "building:part" in tags:
            buildings.append(e)
            continue
        elif "barrier" in tags:
            barriers.append(e)
            continue
        else:
            areas.append(e)
            continue
    else:
        print(f"Ignoring element {e.get('id')} with unknown type {t}")
        continue


############# PHASE 2: Parallel Processing ##############

import multiprocessing

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
    return {"decorations": res, "min_max": (min_x, max_x, min_y, max_y)}

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
        try: layer = int(layer)
        except ValueError: layer = 0
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

def process_nodes(nodes_list, node_id_to_blockpos_local):
    res = defaultdict(list)
    min_x, max_x, min_y, max_y = None, None, None, None
    for node in nodes_list:
        tags = node["tags"]
        deco = None
        if "natural" in tags and tags["natural"] in DECORATIONS: deco = tags["natural"]
        elif "amenity" in tags and tags["amenity"] in DECORATIONS: deco = tags["amenity"]
        elif "barrier" in tags: deco = tags["barrier"] if tags["barrier"] in DECORATIONS else "barrier"
        if not deco: continue
        x, y = get_nodepos(node["lat"], node["lon"])
        min_x = x if min_x is None else min(min_x, x)
        max_x = x if max_x is None else max(max_x, x)
        min_y = y if min_y is None else min(min_y, y)
        max_y = y if max_y is None else max(max_y, y)
        res[deco].append({"x": x, "y": y})
    return {"decorations": res, "min_max": (min_x, max_x, min_y, max_y)}

# Need to pass node_id_to_blockpos to the function, can't be a global for multiprocessing
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


if __name__ == '__main__':
    # sort elements by type (highway, building, area or node)
    for e in data["elements"]:
        t = e["type"]
        tags = e.get("tags")
        if tags and "boundary" in tags.keys():
            continue # ignore boundaries
        if t == "node":
            blockpos = get_nodepos(e["lat"], e["lon"])
            node_id_to_blockpos[e["id"]] = blockpos
            if tags and ("natural" in tags or "amenity" in tags or "barrier" in tags):
                nodes.append(e)
                continue
        elif t == "relation" or t == "multipolygon":
            if not tags:
                continue
            members = e.get("members")
            if not members:
                continue
            if is_area_relation(e):
                split_relation_in_areas_and_holes(e, outer_areas, inner_empty_areas, areas)
                continue
            elif is_building_relation(e):
                split_relation_in_areas_and_holes(e, buildings, buildings, buildings)
                continue
        elif t == "way":
            if not tags:
                continue
            elif "area" in tags:
                areas.append(e)
                continue
            elif "highway" in tags:
                highways.append(e)
                continue
            elif "waterway" in tags:
                if tags['waterway'] in { "ditch", "drain", "stream"}:
                    waterways.append(e)
                continue
            elif "building" in tags or "building:part" in tags:
                buildings.append(e)
                continue
            elif "barrier" in tags:
                barriers.append(e)
                continue
            else:
                areas.append(e)
                continue

    tasks = [
        (process_outer_areas, outer_areas),
        (process_inner_empty_areas, inner_empty_areas),
        (process_areas, areas),
        (process_buildings, buildings),
        (process_barriers, barriers),
        (process_waterways, waterways),
        (process_highways, highways),
        (process_nodes, nodes),
    ]

    final_results = {
        "areas": {"outer": [], "inner": [], "low": [], "medium": [], "high": []},
        "buildings": [],
        "decorations": defaultdict(list),
        "highways": [],
        "waterways": []
    }
    all_min_max = []

    with multiprocessing.Pool() as pool:
        results = [pool.apply_async(func, args=(arg, node_id_to_blockpos)) for func, arg in tasks]
        for r in results:
            res_dict = r.get()
            for key, value in res_dict.items():
                if key == "min_max":
                    if value[0] is not None: # Check if the task produced any coordinates
                        all_min_max.append(value)
                elif key == "areas":
                    for area_key, area_value in value.items():
                        final_results[key][area_key].extend(area_value)
                elif key == "decorations":
                    for deco_key, deco_value in value.items():
                        final_results[key][deco_key].extend(deco_value)
                else:
                    final_results[key].extend(value)

    min_x = min(m[0] for m in all_min_max)
    max_x = max(m[1] for m in all_min_max)
    min_y = min(m[2] for m in all_min_max)
    max_y = max(m[3] for m in all_min_max)

    size_x = max_x - min_x + 1
    size_y = max_y - min_y + 1
    print(f"\nOutput dumped to: {args.output.name}\nfrom {min_x},{min_y} to {max_x},{max_y}: (size: {size_x},{size_y})")

    json.dump({
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "areas": final_results["areas"],
        "buildings": final_results["buildings"],
        "decorations": final_results["decorations"],
        "highways": final_results["highways"],
        "waterways": final_results["waterways"]
    }, args.output, indent=2)

