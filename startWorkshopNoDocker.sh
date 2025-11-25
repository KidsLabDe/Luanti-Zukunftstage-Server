#!/bin/bash

#cd /opt/minetest
ls worlds
read -p "Welche Welt willst Du Starten? (01, 02, 03 etc.) : " world
echo $world
export WORLDNAME=$world
#cp main-config/workshop.conf main-config/minetest.conf
rm mods/world2minetest/map.dat
cp worlds/$WORLDNAME*/world2minetest/map.dat mods/world2minetest/
minetest --server 