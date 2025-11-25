-- concreted/compression.lua

local concrete_nodes = {"concreted:"}

local glass_nodes = {}

if concreted.enable_angledstairs then
    for i = 1, #concreted.angledstairs_subset do
        table.insert(concrete_nodes, concreted.angledstairs_subset[i])
        table.insert(glass_nodes, concreted.angledstairs_subset[i])
    end
end

if concreted.enable_angledwalls then
    for i = 1, #concreted.angledwalls_subset do
        table.insert(concrete_nodes, concreted.angledwalls_subset[i])

        if concreted.angledwalls_subset[i] ~= "angledglass:glass_" then
            table.insert(glass_nodes, concreted.angledwalls_subset[i])
        end
    end
end

if concreted.enable_meseposts then
    table.insert(concrete_nodes, "concreted:mese_post_light_")
end

if concreted.enable_pillars then
    table.insert(concrete_nodes, "pillars:")
end

if concreted.enable_pkarcs then
    table.insert(concrete_nodes, "pkarcs:")
end

if concreted.enable_stairs then
    for i = 1, #concreted.stairs_subset do
        table.insert(concrete_nodes, concreted.stairs_subset[i])
        table.insert(glass_nodes, concreted.stairs_subset[i])
    end
end

if concreted.enable_walls then
    table.insert(concrete_nodes, "concreted:wall_")
end

for i = 1, #concrete_nodes do
    i3.compress(concrete_nodes[i] .. "black_concrete", {
        replace = "black_concrete",
        by = concreted.concrete_list
    })

    if concrete_nodes[i] == "angledglass:glass_" then
        i3.compress(concrete_nodes[i] .. "black_concrete_glass", {
            replace = "black_concrete",
            by = concreted.concrete_list
        })

        i3.compress(concrete_nodes[i] .. "black_concrete_obsidian_glass", {
            replace = "black_concrete",
            by = concreted.concrete_list
        })
    elseif concrete_nodes[i] == "pkarcs:" then
        i3.compress(concrete_nodes[i] .. "black_concrete_arc", {
            replace = "black_concrete",
            by = concreted.concrete_list
        })

        i3.compress(concrete_nodes[i] .. "black_concrete_inner_arc", {
            replace = "black_concrete",
            by = concreted.concrete_list
        })

        i3.compress(concrete_nodes[i] .. "black_concrete_outer_arc", {
            replace = "black_concrete",
            by = concreted.concrete_list
        })
    end
end

if concreted.enable_extensions then
    for i = 1, #glass_nodes do
        i3.compress(glass_nodes[i] .. "black_glass", {
            replace = "black_glass",
            by = concreted.glass_list
        })
    end
end

table.insert(concreted.concrete_list, "black_concrete")

if concreted.enable_moreblocks then
    local concrete, glass
    local moreblocks_nodes_handler = {}

    for i = 1, #concreted.concrete_list do
        concrete = concreted.concrete_list[i]

        moreblocks_nodes_handler[concrete] = {}

        for _, shape in ipairs(concreted.stairsplus_subset) do
            if shape[1] ~= "slope" or shape[2] ~= "" then
                table.insert(
                    moreblocks_nodes_handler[concrete],
                    shape[1] .. "_" .. concrete .. shape[2]
                )
            end
        end

        local slope_name = "slope_" .. concrete

        i3.compress("concreted:" .. slope_name, {
            replace = slope_name,
            by = moreblocks_nodes_handler[concrete],
        })
    end

    if concreted.enable_extensions then
        table.insert(concreted.glass_list, "black_glass")

        for i = 1, #concreted.glass_list do
            glass = concreted.glass_list[i]

            moreblocks_nodes_handler[glass] = {}

            for _, shape in ipairs(concreted.stairsplus_subset) do
                if shape[1] ~= "slope" or shape[2] ~= "" then
                    table.insert(
                        moreblocks_nodes_handler[glass],
                        shape[1] .. "_" .. glass .. shape[2]
                    )
                end
            end

            local slope_name = "slope_" .. glass

            i3.compress("stainedglass:" .. slope_name, {
                replace = slope_name,
                by = moreblocks_nodes_handler[glass],
            })
        end
    end
end

if concreted.enable_stoneworks then
    local concrete
    local stoneworks_nodes_handler = {}

    for i = 1, #concreted.concrete_list do
        concrete = concreted.concrete_list[i]

        stoneworks_nodes_handler[concrete] = {}

        for j = 1, #concreted.stoneworks_subset do
            if concreted.stoneworks_subset[j] ~= "arches_high" then
                table.insert(
                    stoneworks_nodes_handler[concrete],
                    concreted.stoneworks_subset[j] .. "_" .. concrete
                )
            end
        end

        local arches_high_name = "arches_high_" .. concrete

        i3.compress("stoneworks:" .. arches_high_name, {
            replace = arches_high_name,
            by = stoneworks_nodes_handler[concrete]
        })
    end
end
