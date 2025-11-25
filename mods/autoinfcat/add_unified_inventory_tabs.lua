minetest.after(0, function()
    -- get all registered nodes
    local node_table = minetest.registered_nodes
    local mods_with_nodes = {}
    for node, attr in pairs(node_table) do
        -- sort out stuff which is not in the creative inventory
        if not attr['groups']['not_in_creative_inventory'] then
            -- get their mod name
            local mod_name = string.split(node,':')[1]

            -- collect them in a table
            if mods_with_nodes[mod_name] == nil then
                mods_with_nodes[mod_name] = {}
            end

            table.insert(mods_with_nodes[mod_name], node)
        end
        
    end

    -- add them to unified inventory
    local min_registrations_per_mod = 10
    local nodes_with_not_enough_siblings = {}
    for mod, nodes in pairs(mods_with_nodes) do
        if #nodes < min_registrations_per_mod then
            for _, node in pairs(nodes) do
                -- print('what is nodes', type(nodes), dump(nodes))
                table.insert(nodes_with_not_enough_siblings, node)
            end
        else
            -- print("mod", type(mod), mod)
            unified_inventory.register_category(mod, {
                -- symbol = "autoinvcat_cat_".. mod:sub(1,1) ..".png", -- TODO: find mod symbol
                symbol = cat_icon(mod),
                -- ^ Can be in the format "mod_name:item_name" or "texture.png",
                label = mod, -- TODO: find appropriate label
                index = string_to_numer_alphabetical_order(mod),
                -- ^ Categories are sorted by index. Lower numbers appear before higher ones.
                --   By default, the name is translated to a number: AA -> 0.0101, ZZ -> 0.2626
                ---  Predefined category indices: "all" = -2, "uncategorized" = -1
                items = nodes
                -- ^ List of items within this category
            })
        end
    end

    -- group small mods with les then min_registrations_per_mod (e.g. 10) nodes in 1 category
    unified_inventory.register_category("Misc.", {
        symbol = "autoinvcat_misc.png", -- TODO: find mod symbol
        -- ^ Can be in the format "mod_name:item_name" or "texture.png",
        label = "Misc. nodes label", -- TODO: find appropriate label
        index = 100, 
        -- ^ Categories are sorted by index. Lower numbers appear before higher ones.
        --   By default, the name is translated to a number: AA -> 0.0101, ZZ -> 0.2626
        ---  Predefined category indices: "all" = -2, "uncategorized" = -1
        items = nodes_with_not_enough_siblings
        -- ^ List of items within this category
    })

end)

