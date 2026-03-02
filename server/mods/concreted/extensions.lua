-- concreted/extensions.lua

local color_name, color_desc
local S = minetest.get_translator("concreted")

for i = 1, #concreted.colors do
    color_name, color_desc = unpack(concreted.colors[i])

    if concreted.enable_angledstairs then
        angledstairs.register_angled_stair_and_angled_slab(
            "_" .. color_name .. "_glass",
            "stainedglass:" .. color_name .. "_glass",
            {cracky = 3, oddly_breakable_by_hand = 2},
            {"stainedglass_" .. color_name .. ".png"},
            S("@1 Angled Stair", S("@1 Glass", S(color_desc))),
            S("@1 Angled Slab", S("@1 Glass", S(color_desc))),
            default.node_sound_glass_defaults()
        )
    end

    if concreted.enable_angledwalls then
        angledwalls.register_angled_wall_and_low_angled_wall_and_corner(
            "_" .. color_name .. "_glass",
            "stainedglass:" .. color_name .. "_glass",
            {cracky = 3, oddly_breakable_by_hand = 2},
            {"stainedglass_" .. color_name .. ".png"},
            S("@1 Angled Wall", S("@1 Glass", S(color_desc))),
            S("@1 Low Angled Wall", S("@1 Glass", S(color_desc))),
            S("@1 Corner", S("@1 Glass", S(color_desc))),
            default.node_sound_glass_defaults()
        )

        slopedwalls.register_sloped_wall(
            "_" .. color_name .. "_glass",
            "stainedglass:" .. color_name .. "_glass",
            {cracky = 3, oddly_breakable_by_hand = 2},
            {"stainedglass_" .. color_name .. ".png"},
            S("@1 Sloped Wall", S("@1 Glass", S(color_desc))),
            default.node_sound_glass_defaults()
        )
    end

    if concreted.enable_moreblocks then
        stairsplus:register_custom_subset(
		    concreted.stairsplus_subset,
		    "stainedglass",
		    color_name .. "_glass",
		    "stainedglass:stained_glass_" .. color_name,
		    {
			    description = S("@1 Glass", S(color_desc)),
			    groups = {cracky = 3, oddly_breakable_by_hand = 2},
			    sounds = default.node_sound_glass_defaults(),
			    tiles = {"stainedglass_" .. color_name .. ".png"},
		    }
	    )
    end

    if concreted.enable_stairs then
        stairs.register_stair_and_slab(
            color_name .. "_glass",
		    "stainedglass:stained_glass_" .. color_name,
		    {cracky = 3, oddly_breakable_by_hand = 2},
		    {"stainedglass_" .. color_name .. ".png"},
		    S("@1 Stair", S("@1 Glass", S(color_desc))),
		    S("@1 Slab", S("@1 Glass",  S(color_desc))),
		    default.node_sound_glass_defaults(),
		    false,
		    S("Inner @1", S("@1 Stair", S("@1 Glass", S(color_desc)))),
		    S("Outer @1", S("@1 Stair", S("@1 Glass", S(color_desc))))
        )
    end

    if color_name ~= "black" then
        table.insert(concreted.glass_list, color_name .. "_glass")
    end
end
