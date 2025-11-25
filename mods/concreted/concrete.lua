-- concreted/concrete.lua

local dye_craft
local S = minetest.get_translator("concreted")

function concreted.register_craft(color_name)
    dye_craft = "group:dye,color_" .. color_name

    for _, container in pairs(concreted.water_containers) do
        minetest.register_craft({
            output = "concreted:" .. color_name .. "_concrete 6",
            recipe = {
                {"group:sand",     "group:sand",     "group:sand"},
                {dye_craft,        container[2],     dye_craft},
                {"default:gravel", "default:gravel", "default:gravel"}
            },
            replacements = {{container[2], container[1]}},
            type = "shaped"
        })
    end
end

function concreted.register_mesepost(color_name, color_desc)
    default.register_mesepost(
		"concreted:mese_post_light_" .. color_name .. "_concrete",
		{
			description = S("@1 Mese Post Light", S("@1 Concrete", S(color_desc))),
			material = "concreted:" .. color_name .. "_concrete",
			texture = "concreted_" .. color_name .. ".png"
		}
	)
end

function concreted.register_node(color_name, color_desc)
    minetest.register_node(
        "concreted:" .. color_name .. "_concrete",
        {
            description = S("@1 Concrete", S(color_desc)),
            is_ground_content = false,
            groups = {concrete = 1, cracky = 2},
            sounds = default.node_sound_stone_defaults(),
            tiles = {"concreted_" .. color_name .. ".png"}
        }
    )

	concreted.register_craft(color_name)
end

function concreted.register_stair_and_slab(color_name, color_desc)
    stairs.register_stair_and_slab(
		color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2},
		{"concreted_" .. color_name .. ".png"},
		S("@1 Stair", S("@1 Concrete", S(color_desc))),
		S("@1 Slab", S("@1 Concrete",  S(color_desc))),
		default.node_sound_stone_defaults(),
		false,
		S("Inner @1", S("@1 Stair", S("@1 Concrete", S(color_desc)))),
		S("Outer @1", S("@1 Stair", S("@1 Concrete", S(color_desc))))
	)
end

function concreted.register_walls(color_name, color_desc)
    walls.register(
		"concreted:wall_" .. color_name .. "_concrete",
		S("@1 Wall", S("@1 Concrete", S(color_desc))),
		"concreted_" .. color_name .. ".png",
		"concreted:" .. color_name .. "_concrete",
		default.node_sound_stone_defaults()
	)
end
