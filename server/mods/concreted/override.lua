-- concreted/override.lua

local S = minetest.get_translator("concreted")

if concreted.enable_meseposts then
    for i = 1, #concreted.colors do
        minetest.override_item(
            "concreted:mese_post_light_" .. concreted.colors[i][1] .. "_concrete",
            {
                groups = {cracky = 3, oddly_breakable_by_hand = 2},
                sounds = default.node_sound_stone_defaults()
            }
        )
    end
end

if concreted.enable_renaming then
    local node_shape, node_info, node_desc, color_name, color_desc

    if concreted.enable_moreblocks then
        for i = 1, #concreted.stairsplus_subset do
            node_shape = concreted.stairsplus_subset[i][1]
            node_info = concreted.stairsplus_subset[i][2]
            node_desc = node_shape:sub(1, 1):upper() .. node_shape:sub(2)

            if node_shape == "micro" then
                node_desc = node_desc .. "block"
            end

            for j = 1, #concreted.colors do
                color_name, color_desc = unpack(concreted.colors[j])
                if concreted.stairsplus_subset[i][2] ~= "" then
                    minetest.override_item(
                        "concreted:" .. node_shape .. "_" .. color_name .. "_concrete" .. node_info,
                        {
                            description = S("@1 " .. node_desc, S("@1 Concrete", S(color_desc))),
                        }
                    )

                    if concreted.enable_extensions then
                        minetest.override_item(
                            "stainedglass:" .. node_shape .. "_" .. color_name .. "_glass" .. node_info,
                            {
                                description = S("@1 " .. node_desc, S("@1 Glass", S(color_desc))),
                            }
                        )
                    end
                else
                    minetest.override_item(
                        "concreted:" .. node_shape .. "_" .. color_name .. "_concrete",
                        {
                            description = S("@1 " .. node_desc, S("@1 Concrete", S(color_desc)))
                        }
                    )

                    if concreted.enable_extensions then
                        minetest.override_item(
                            "stainedglass:" .. node_shape .. "_" .. color_name .. "_glass",
                            {
                                description = S("@1 " .. node_desc, S("@1 Glass", S(color_desc))),
                            }
                        )
                    end
                end
            end
        end
    end

    if concreted.enable_pkarcs then
        for i = 1, #concreted.colors do
            minetest.override_item(
                "pkarcs:" .. concreted.colors[i][1] .. "_concrete_arc",
                {
                    description = S("@1 Arc", S("@1 Concrete", S(concreted.colors[i][2])))
                }
            )

            minetest.override_item(
                "pkarcs:" .. concreted.colors[i][1] .. "_concrete_inner_arc",
                {
                    description = S("Inner @1", S("@1 Arc", S("@1 Concrete", S(concreted.colors[i][2]))))
                }
            )

            minetest.override_item(
                "pkarcs:" .. concreted.colors[i][1] .. "_concrete_outer_arc",
                {
                    description = S("Outer @1", S("@1 Arc", S("@1 Concrete", S(concreted.colors[i][2]))))
                }
            )
        end
    end
end
