minetest.set_mapgen_setting("mg_name", "singlenode", true)

local air = minetest.get_content_id("air")
local underground_stone = minetest.get_content_id("mcl_core:stone")

-- Ground & Stone Materials
local default_ground = minetest.get_content_id("basic_materials:cement_block")
local gravel_ground = minetest.get_content_id("mcl_core:gravel")
local stone_slab_block = minetest.get_content_id("mcl_core:stone")
local paving_stone = minetest.get_content_id("mcl_core:stonebrick")
local residential_area_ground = minetest.get_content_id("mcl_core:cobble")

-- Water
local water_source = minetest.get_content_id("mcl_core:water_source")

-- Surface Materials
local grass_ground = minetest.get_content_id("mcl_core:dirt_with_grass")
local dry_grass_ground = minetest.get_content_id("mcl_lush_caves:rooted_dirt")
local playground_sand = minetest.get_content_id("mcl_core:sand")
local pitch_sand = minetest.get_content_id("mcl_core:redsand")

-- Roads & Hard Surfaces
local concrete_surface = minetest.get_content_id("mcl_colorblocks:concrete_silver")
local asphalt_surface = minetest.get_content_id("mcl_colorblocks:concrete_grey")

-- Building Materials
local building_walls = minetest.get_content_id("mcl_core:sandstonesmooth2")
local building_roof = minetest.get_content_id("mcl_core:brick_block")
local building_foundation = minetest.get_content_id("mcl_trees:tree_oak")

-- Decoration Materials
local hedge_leaves = minetest.get_content_id("mcl_trees:leaves_oak")
local tall_grass = minetest.get_content_id("mcl_flowers:tallgrass")
local wooden_fence = minetest.get_content_id("mcl_fences:oak_fence")
local wooden_gate = minetest.get_content_id("mcl_fences:oak_fence_gate")
local bench_stair = minetest.get_content_id("mcl_stairs:stair_oak")
local cobble_wall = minetest.get_content_id("mcl_walls:cobble")
local sandstone_wall = minetest.get_content_id("mcl_walls:sandstone")

-- Special/Utility Blocks
local post_box_block = minetest.get_content_id("mcl_core:goldblock")
local recycling_block = minetest.get_content_id("mcl_copper:block")
local vending_machine_block = minetest.get_content_id("mcl_core:ironblock")
local telephone_block = minetest.get_content_id("mcl_core:diamondblock")

-- Highway/Road Variables
local highway_default = default_ground
local highway_footway = minetest.get_content_id("mcl_colorblocks:concrete_powder_silver")
local highway_service = highway_default
local highway_cycleway = minetest.get_content_id("mcl_colorblocks:hardened_clay_pink")
local highway_pedestrian = highway_footway
local highway_residential = minetest.get_content_id("basic_materials:cement_block")
local highway_path = minetest.get_content_id("mcl_colorblocks:hardened_clay_grey")

-- Leisure Variables
local leisure_default = grass_ground
local leisure_park = grass_ground
local leisure_playground = playground_sand
local leisure_sports_centre = grass_ground
local leisure_pitch = pitch_sand

-- Amenity Variables
local amenity_default = stone_slab_block
local amenity_school = stone_slab_block
local amenity_parking = underground_stone

-- Landuse Variables
local landuse_default = default_ground
local landuse_residential = residential_area_ground
local landuse_village_green = grass_ground

-- Natural Variables
local natural_default = grass_ground
local natural_water = water_source

-- Building Variables
local surface_building_ground = building_foundation
local surface_grass = grass_ground

-- Decoration Natural Variables
local decoration_natural_default = hedge_leaves
local decoration_natural_grass = tall_grass

-- Decoration Barrier Variables
local decoration_barrier_default = cobble_wall
local decoration_barrier_fence = wooden_fence
local decoration_barrier_wall = cobble_wall
local decoration_barrier_bollard = sandstone_wall
local decoration_barrier_gate = wooden_gate
local decoration_barrier_hedge = hedge_leaves

-- Decoration Amenity Variables
local decoration_amenity_post_box = post_box_block
local decoration_amenity_recycling = recycling_block
local decoration_amenity_vending_machine = vending_machine_block
local decoration_amenity_bench = bench_stair
local decoration_amenity_telephone = telephone_block

local SURFACE_IDS = {
	[0] = default_ground, -- default
	--surface
	[1] = paving_stone, -- paving stones
	[2] = gravel_ground, -- fine gravel
	[3] = concrete_surface, -- concrete
	[4] = asphalt_surface, -- asphalt
	[5] = default_ground, -- dirt
	-- highway
	[10] = highway_default, -- default
	[11] = highway_footway, -- footway
	[12] = highway_service, -- service
	[13] = highway_cycleway, -- cycleway
	[14] = highway_pedestrian, -- pedestrian
	[15] = highway_residential, -- residential
	[16] = highway_path, -- path
	-- leisure
	[20] = leisure_default, -- default
	[21] = leisure_park, -- park
	[22] = leisure_playground, -- playground
	[23] = leisure_sports_centre, -- sports centre
	[24] = leisure_pitch, -- pitch
	-- amenity
	[30] = amenity_default, -- default
	[31] = amenity_school, -- school
	[32] = amenity_parking, -- parking
	-- landuse
	[40] = landuse_default, -- default
	[41] = landuse_residential, -- residential_landuse
	[42] = landuse_village_green, -- village_green
	-- natural
	[50] = natural_default, -- default
	[51] = natural_water, -- water

	[60] = surface_building_ground, -- building_ground
	[70] = surface_grass, -- grass
}

local DECORATION_IDS = {
	[0] = minetest.get_content_id("air"), -- default
	-- natural
	[10] = decoration_natural_default, -- default
	[11] = decoration_natural_grass, -- grass
	-- amenity
	[21] = decoration_amenity_post_box, -- post box
	[22] = decoration_amenity_recycling, -- recycling
	[23] = decoration_amenity_vending_machine, -- vending machine
	[24] = decoration_amenity_bench, -- bench
	[25] = decoration_amenity_telephone, -- telephone
	-- barrier
	[30] = decoration_barrier_default, -- default
	[31] = decoration_barrier_fence, -- fence
	[32] = decoration_barrier_wall, -- wall
	[33] = decoration_barrier_bollard, -- bollard
	[34] = decoration_barrier_gate, -- gate
	[35] = decoration_barrier_hedge, -- hedge
}

local DECORATION_SCHEMATICS = {
	--[12] = {schematic=minetest.get_modpath("default") .. "/schematics/apple_tree.mts", rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- tree
	--[13] = {schematic=minetest.get_modpath("default") .. "/schematics/apple_tree.mts", rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- leaf_tree
	--[14] = {schematic=minetest.get_modpath("default") .. "/schematics/pine_tree.mts",  rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- conifer
	--[15] = {schematic=minetest.get_modpath("default") .. "/schematics/bush.mts",       rotation="random", force_placement=false, flags="place_center_x, place_center_z", shift_y=-1}, -- bush
}

local layer_count = nil
local floor_height = nil
local offset_x = nil
local offset_z = nil
local width = nil
local height = nil
local map = nil
local incr = nil

local function bytes2int(str, signed) -- little endian
	-- copied from https://github.com/Gael-de-Sailly/geo-mapgen/blob/4bacbe902e7c0283a24ee3efa35c283ad592e81c/init.lua#L33
	local bytes = { str:byte(1, -1) }
	local n = 0
	local byte_val = 1
	for _, byte in ipairs(bytes) do
		n = n + (byte * byte_val)
		byte_val = byte_val * 256
	end
	if signed and n >= byte_val / 2 then
		return n - byte_val
	end
	return n
end

local modpath = minetest.get_modpath(minetest.get_current_modname())

local function get_layers(x, z)
	x = x + offset_x
	z = z + offset_z
	if x < 0 or z < 0 or x >= width or z >= height then
		return 0, 0, 0
	end
	local i = z * width * layer_count + x * layer_count + 1
	return bytes2int(map:sub(i, i)),
		bytes2int(map:sub(i + 1, i + 1)),
		bytes2int(map:sub(i + 2, i + 2)),
		bytes2int(map:sub(i + 3, i + 3))
end

local function load_map_file()
	-- local path = modpath .. "/" .. "map.dat"
	local path = minetest.get_worldpath() .. "/world2minetest/map.dat"
	minetest.log("[w2mt] Loading map.dat from " .. path)
	local file = io.open(path, "rb")

	local CURRENT_VERSION = 1

	local version = bytes2int(file:read(1))
	local min_compat_version = bytes2int(file:read(1))
	if min_compat_version > CURRENT_VERSION then
		error("world2minetest can't load map.dat")
		--        error("world2minetest can't load map.dat (version " .. version .. ", needs version " .. min_compat_version .. " or higher (mod version: " .. CURRENT_VERSION .. ")")
	end
	if version ~= CURRENT_VERSION then
		minetest.log("[w2mt] WARNING: map.dat has newer version ") -- .. version .. " (mod version: " .. CURRENT_VERSION .. ")")
	end
	layer_count = bytes2int(file:read(1))
	floor_height = -bytes2int(file:read(1))
	offset_x = bytes2int(file:read(2))
	offset_z = bytes2int(file:read(2))
	width = bytes2int(file:read(2))
	height = bytes2int(file:read(2))
	local map_size = bytes2int(file:read(4))
	map = minetest.decompress(file:read(map_size))
	local incr_size = bytes2int(file:read(4))
	local incr_info
	if incr_size ~= 0 then
		incr = minetest.decompress(file:read(incr_size))
		incr_info = " incr mapblocks:" .. incr:len() / 4
	else
		incr_info = " no incr data"
	end
	-- minetest.log("[w2mt] map.dat loaded! offset_x:" .. offset_x .. " offset_z:" .. offset_z .. " width:" .. width .. " height:" .. height .. " len:" .. map:len() .. incr_info)
end

load_map_file()

local vdata = {}
local function generate(vm, emin, emax, minp, maxp)
	-- minetest.log("[w2mt] generate(vm:" .. vm .. ",emin:" .. emin .. ",emax:" .. emax .. ",minp:" .. minp.. ",maxp:" .. maxp)
	vm:get_data(vdata)
	local va = VoxelArea:new({ MinEdge = emin, MaxEdge = emax })
	local schematics_to_place = {}
	for x = minp.x, maxp.x do
		for z = minp.z, maxp.z do
			local i = va:index(x, minp.y, z)
			-- for a description of these layers, see generate_map.py
			local y0_height, surface_id, y1_decoration_id, y2_max_building = get_layers(x, z)
			local stone_min = minp.y
			local stone_max = math.min(floor_height + y0_height - 1, maxp.y)
			local surface_y = floor_height + y0_height
			local decoration_y = surface_y + 1

			if stone_min <= stone_max then
				for _ = stone_min, stone_max do
					vdata[i] = underground_stone
					i = i + va.ystride
				end
			end

			if minp.y <= surface_y and surface_y <= maxp.y then
				vdata[i] = SURFACE_IDS[surface_id]
				i = i + va.ystride
			end

			if x == 0 and z == 0 then
				-- place a sign with credits
				if minp.y <= decoration_y and decoration_y <= maxp.y then
					table.insert(schematics_to_place, { pos = { x = 0, y = decoration_y, z = 0 }, id = "credit_sign" })
				end
			elseif y1_decoration_id >= 128 then
				-- there's a building here
				local has_roof
				local roof_adjustment = 0
				
				if y2_max_building >= 128 then
					-- Building has a roof: subtract 127 to decode, then 1 more for roof
					y2_max_building = y2_max_building - 127
					roof_adjustment = 1
					has_roof = true
				else
					-- Building has no roof: just decode
					y2_max_building = y2_max_building
					roof_adjustment = 0
					has_roof = false
				end
				
				-- Decode the starting height (floor of building)
				y1_decoration_id = floor_height + y1_decoration_id - 127
				-- Calculate the top floor height (NOT including roof)
				local building_top_y = floor_height + y2_max_building - roof_adjustment
				
				-- building from y1_decoration_id to building_top_y
				local building_min = math.max(y1_decoration_id, minp.y)
				local building_max = math.min(building_top_y, maxp.y)
				i = va:index(x, building_min, z)
				if building_min <= building_max then
					for _ = building_min, building_max do
						vdata[i] = building_walls
						i = i + va.ystride
					end
				end
				
				if has_roof then
					local roof_y = building_top_y + 1
					if minp.y <= roof_y and roof_y <= maxp.y then
						-- Calculate fresh index for roof position
						local roof_i = va:index(x, roof_y, z)
						vdata[roof_i] = building_roof
					end
				end
			else
				if minp.y <= decoration_y and decoration_y <= maxp.y then
					if 12 <= y1_decoration_id and y1_decoration_id <= 15 then
						-- HIER NICHTS TUN (Bäume deaktiviert für Mineclonia)
						-- table.insert(schematics_to_place, {pos={x=x, y=decoration_y, z=z}, id=y1_decoration_id})
					else
						vdata[i] = DECORATION_IDS[y1_decoration_id]
					end
				end
			end
		end
	end

	vm:set_data(vdata)
	for _, s in pairs(schematics_to_place) do
		if s.id == "credit_sign" then
			-- Place Mineclonia Sign
			-- Use wall sign with param2 for direction (0-3)
			minetest.set_node(s.pos, { name = "mcl_signs:wall_sign", param2 = 1 })

			local meta = minetest.get_meta(s.pos)
			meta:set_string(
				"text",
				"This world has been created with world2minetest by Florian Rädiker. See github.com/FlorianRaediker/world2minetest for the source code (AGPLv3)."
			)
		else
			local info = DECORATION_SCHEMATICS[s.id]
			if info.shift_y then
				s.pos.y = s.pos.y + info.shift_y
			end
			minetest.place_schematic_on_vmanip(
				vm, -- vmanip
				s.pos, -- pos
				info.schematic, -- schematic
				info.rotation, -- rotation
				info.replacement, -- replacement
				info.force_placement, -- force_placement
				info.flags -- flags
			)
		end
	end
	vm:update_liquids()
	vm:calc_lighting()
	vm:write_to_map()
end

minetest.register_on_generated(function(minp, maxp, blockseed)
	local vm, emin, emax = minetest.get_mapgen_object("voxelmanip")
	generate(vm, emin, emax, minp, maxp)
end)

minetest.register_chatcommand("w2mt:incr", {
	privs = {
		server = true,
	},
	func = function(name, param)
		if incr == nil then
			minetest.log("[w2mt] No incremental data available")
		end
		load_map_file()
		local len = string.len(incr) / 4
		for i = 0, len - 1 do
			local start_i = i * 4
			local block_x = bytes2int(incr:sub(start_i + 1, start_i + 2), true)
			local block_z = bytes2int(incr:sub(start_i + 3, start_i + 4), true)
			local node_x_min = block_x * 16
			local node_x_max = node_x_min + 15
			local node_z_min = block_z * 16
			local node_z_max = node_z_min + 15
			-- minetest.log("[w2mt] Deleting mapblock " .. i+1 .. "/" .. len .. ": (" .. block_x .. "," .. block_z .. ") from (" .. node_x_min .. "," .. node_z_min .. ") to (" .. node_x_max .. "," .. node_z_max .. ")")
			minetest.delete_area(
				{ x = node_x_min, y = floor_height, z = node_z_min },
				{ x = node_x_max, y = floor_height + 255, z = node_z_max }
			)
		end
	end,
})

minetest.register_chatcommand("w2mt:generateall", {
	privs = {
		server = true,
	},
	func = function(name, param)
		local min_x = -offset_x - 128
		local max_x = min_x + width + 256
		local min_z = -offset_z - 128
		local max_z = min_z + height + 256

		local vm = nil

		local x = min_x
		local count = 0
		local start = tonumber(param)
		if not start then
			start = 1
		end
		local end_ = start + 499
		while x + 79 <= max_x do
			local z = min_z
			while z + 79 <= max_z do
				count = count + 1
				if count >= start and count <= end_ then
					local minp = { x = x, y = floor_height - 10, z = z }
					local maxp = { x = x + 79, y = minp.y + 280, z = z + 79 }
					vm = minetest.get_voxel_manip(minp, maxp)
					local emin, emax = vm:read_from_map(minp, maxp)
					generate(vm, emin, emax, minp, maxp)
				end
				z = z + 80
			end
			x = x + 80
		end
		-- minetest.log("[w2mt] Generated map from " .. start .. " to " .. end_ .. " (total: " .. count .. ")")
	end,
})