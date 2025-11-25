function string_to_numer_alphabetical_order(str)
    -- returns a number between 101 and 127
    -- order of the returned numbers is the same as the alphabetical order of the input strings
    str = string.lower(str)
    local number = 100
    -- print()
    for i = 1, #str do
        local c = str:sub(i,i)
	--print(c)
	local c_num = char_to_num(c)
	--print(c_num)
	local scaled = c_num / (char_to_num('z')+1)^(i-1)
	--print(char_to_num('z'))
	--print(scaled)
	number = number + scaled
    end
    return number
end

function char_to_num(c)
	-- 'a' = 1; 'b' = 2; ...  'z' = 26
	return tonumber(c, 36)-9
end

--- test cases
-- print(string_to_numer_alphabetical_order('a'))
-- print(string_to_numer_alphabetical_order('aa'))
-- print(string_to_numer_alphabetical_order('aaa'))
-- print(string_to_numer_alphabetical_order('aaaaaaa'))
-- print(string_to_numer_alphabetical_order('azzzzzz'))
-- print(string_to_numer_alphabetical_order('b'))
-- print(string_to_numer_alphabetical_order('ba'))
-- print(string_to_numer_alphabetical_order('bzz'))
-- print(string_to_numer_alphabetical_order('caaaa'))
-- print(string_to_numer_alphabetical_order('caaab'))
-- print(string_to_numer_alphabetical_order('y'))
-- print(string_to_numer_alphabetical_order('zz'))
-- print(string_to_numer_alphabetical_order('zzzzzzzzzzzzzz'))

local texture_listing = minetest.get_dir_list(MODPATH.."/textures")
function cat_icon(category_name)
    local first_char = string.lower(category_name):sub(1,1)
    if file_exists(MODPATH.."/textures/autoinvcat_cat_".. first_char .. ".png") then
        return "autoinvcat_cat_".. first_char .. ".png"
    end
    return "autoinvcat_fallback.png"
end

function file_exists(name)
    local f=io.open(name,"r")
    if f~=nil then io.close(f) return true else return false end
end
 