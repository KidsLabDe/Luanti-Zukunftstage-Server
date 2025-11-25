# Minetest Game mod: concreted <h1>

The Default Concrete mod adds colored concrete blocks to the game.
By default, the concrete colors available are the colors of the Dye mod.
Each concrete color has stair, slab, and wall variants.
The main idea behind this mod is to add colored blocks that match the colors of the Wool mod.
The texture of the blocks is still very simple, but I intend to change that.


## Concrete craft recipe <h2>
### Bucket <h3>
~~~lua
    {
        {"group:sand", "group:sand", "group:sand"},
        {"group:dye", "bucket:bucket_water", "group:dye"},
        {"default:gravel", "default:gravel", "default:gravel"}

        {"group:sand", "group:sand", "group:sand"},
        {"group:dye", "bucket:bucket_river_water", "group:dye"},
        {"default:gravel", "default:gravel", "default:gravel"}
    }
~~~


### Wooden Bucket <h3>
~~~lua
    {
        {"group:sand", "group:sand", "group:sand"},
        {"group:dye", "bucket_wooden:bucket_water", "group:dye"},
        {"default:gravel", "default:gravel", "default:gravel"}

        {"group:sand", "group:sand", "group:sand"},
        {"group:dye", "bucket_wooden:bucket_river_water", "group:dye"},
        {"default:gravel", "default:gravel", "default:gravel"}
    }
~~~


## Dependencies
* Bucket
* Default
* Dye
* Stairs
* Walls


## Optional dependencies <h2>
* [Angled Stairs](https://content.minetest.net/packages/TumeniNodes/angledstairs/)
* [Angled Walls](https://content.minetest.net/packages/TumeniNodes/angledwalls/)
* [i3](https://content.minetest.net/packages/jp/i3/)
* [More Blocks](https://content.minetest.net/packages/Calinou/moreblocks/)
* [Pillars](https://content.minetest.net/packages/citorva/pillars/)
* [pkarcs](https://content.minetest.net/packages/TumeniNodes/pkarcs/)
* [Stained Glass](https://content.minetest.net/packages/alerikaisattera/stainedglass/)
* [Stoneworks](https://content.minetest.net/packages/TumeniNodes/stoneworks/)\*
* [Wooden Bucket](https://content.minetest.net/packages/Hume2/bucket_wooden/)


## Compatibility extension <h2>
* Angled Stairs + Stained Glass
* Angled Walls + Stained Glass
* More Blocks + Stained Glass
* i3 compression for all new additions

-------------------------------------------------------------------------------
>(\*) **NOTE**: Partially working, due to problems with the function ```stoneworks.register_thin_wall()```

-------------------------------------------------------------------------------
## Mod settings <h2>

All of these settings are enabled by default. You can disable them in the settings tab of the main menu.

```enable_angledstairs``` <br>
```enable_angledwalls``` <br>
```enable_bucket_wooden``` <br>
```enable_compression``` <br>
```enable_extensions``` <br>
```enable_moreblocks``` <br>
```enable_meseposts``` <br>
```enable_pillars``` <br>
```enable_pkarcs``` <br>
```enable_stairs``` <br>
```enable_stoneworks``` <br>
```enable_walls``` <br>

-------------------------------------------------------------------------------
## License <h2>
See **license.txt** for license information

### Authors of source code <h3>
>Originally by Perttu Ahola (celeron55) <celeron55@gmail.com> (MIT)
>
>Various Minetest developers and contributors (MIT)
>
>José Douglas (dougsouza26) (MIT)


### Authors of media (textures) <h3>
>José Douglas (CC BY-SA 3.0):

    concreted_black.png,  concreted_blue.png,       concreted_brown.png,
    concreted_cyan.png,   concreted_dark_green.png, concreted_dark_grey.png,
    concreted_green.png,  concreted_grey.png,       concreted_magenta.png,
    concreted_orange.png, concreted_pink.png,       concreted_red.png
    concreted_violet.png, concreted_white.png,      concreted_yellow.png


The texture pack uses colors obtained from the wool texture pack.

>Credits for wool texture pack: Cisoun  (CC BY-SA 3.0)

