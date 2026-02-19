-- concreted/init.lua

concreted = {}

local color_name, color_desc
local path = minetest.get_modpath("concreted")

dofile(path .. "/compatibles.lua")
dofile(path .. "/concrete.lua")
dofile(path .. "/definitions.lua")

if concreted.enable_bucket_wooden then
	table.insert(
		concreted.water_containers,
		{"bucket_wooden:bucket_empty", "bucket_wooden:bucket_water"}
	)

	table.insert(
		concreted.water_containers,
		{"bucket_wooden:bucket_empty", "bucket_wooden:bucket_river_water"}
	)
end

for i = 1, #concreted.colors do
	color_name, color_desc = unpack(concreted.colors[i])

	concreted.register_node(color_name, color_desc)

	concreted.angledstairs(color_name, color_desc)

	concreted.angledwalls(color_name, color_desc)

	concreted.meseposts(color_name, color_desc)

	concreted.moreblocks(color_name, color_desc)

	concreted.pillars(color_name, color_desc)

	concreted.pkarcs(color_name, color_desc)

	concreted.stairs(color_name, color_desc)

	concreted.stoneworks(color_name, color_desc)

	concreted.walls(color_name, color_desc)

	if color_name ~= "black" then
		table.insert(concreted.concrete_list, color_name .. "_concrete")
	end
end

if concreted.enable_extensions then
	dofile(path .. "/extensions.lua")
end

if concreted.enable_compression then
	dofile(path .. "/compression.lua")
end

dofile(path .. "/override.lua")

