-- concreted/compatibles.lua

local S = minetest.get_translator("concreted")

function concreted.register_angledstairs(color_name, color_desc)
    angledstairs.register_angled_stair_and_angled_slab(
		"_" .. color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2},
		{"concreted_" .. color_name .. ".png"},
		S("@1 Angled Stair", S("@1 Concrete", S(color_desc))),
		S("@1 Angled Slab", S("@1 Concrete", S(color_desc))),
		default.node_sound_stone_defaults()
	)
end

function concreted.register_angledwalls(color_name, color_desc)
    angledglass.register_glass(
		"_" .. color_name .. "_concrete_glass",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2, oddly_breakable_by_hand = 1},
		{"default_glass.png", "concreted_" .. color_name .. ".png"},
		S("@1 With Glass", S("@1 Concrete", S(color_desc))),
		default.node_sound_glass_defaults()
	)

	angledglass.register_glass(
		"_" .. color_name .. "_concrete_obsidian_glass",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2, oddly_breakable_by_hand = 1},
		{"default_obsidian_glass.png", "concreted_" .. color_name .. ".png"},
		S("@1 Obsidian Glass", S("@1 Concrete", S(color_desc))),
		default.node_sound_glass_defaults()
	)

	angledwalls.register_angled_wall_and_low_angled_wall_and_corner(
		"_" .. color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2},
		{"concreted_" .. color_name .. ".png"},
		S("@1 Angled Wall", S("@1 Concrete", S(color_desc))),
		S("@1 Low Angled Wall", S("@1 Concrete", S(color_desc))),
		S("@1 Corner", S("@1 Concrete", S(color_desc))),
		default.node_sound_stone_defaults()
	)

	slopedwalls.register_sloped_wall(
		"_" .. color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2},
		{"concreted_" .. color_name .. ".png"},
		S("@1 Sloped Wall", S("@1 Concrete", S(color_desc))),
		default.node_sound_stone_defaults()
	)
end

function concreted.register_moreblocks(color_name, color_desc)
    stairsplus:register_custom_subset(
		concreted.stairsplus_subset,
		"concreted",
		color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{
			description = S("@1 Concrete", S(color_desc)),
			groups = {cracky = 2},
			sounds = default.node_sound_stone_defaults(),
			tiles = {"concreted_" .. color_name .. ".png"},
		}
	)
end

function concreted.register_pillars(color_name, color_desc)
    pillars.register_pillar(
        color_name .. "_concrete",
        {
            basenode = "concreted:" .. color_name .. "_concrete",
            description = S("@1 Pillar", S("@1 Concrete", S(color_desc))),
            groups = {cracky = 2},
            sounds = default.node_sound_stone_defaults(),
            sunlight_propagates = true,
            textures = {"concreted_" .. color_name .. ".png"},
        }
    )
end

function concreted.register_pkarcs(color_name, color_desc)
    pkarcs.register_all(
		color_name .. "_concrete",
		S("@1 Concrete", S(color_desc)),
		{"concreted_" .. color_name .. ".png"},
		default.node_sound_stone_defaults(),
		{cracky = 2},
		"concreted:" .. color_name .. "_concrete"
	)
end

function concreted.register_stoneworks(color_name, color_desc)
    stoneworks.register_arches(
		"_" .. color_name .. "_concrete",
		"concreted:" .. color_name .. "_concrete",
		{cracky = 2},
		{"concreted_" .. color_name .. ".png"},
		S("@1 Arches", S("@1 Concrete", S(color_desc))),
		default.node_sound_stone_defaults()
	)
end
