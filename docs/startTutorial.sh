#!/bin/bash
# cd /opt/minetest
cp server/config/tutorial.conf server/config/minetest.conf
rm debug.txt
#rm -R /opt/minetest-zfn-docker/worlds/Tutorial
#cp -R /opt/minetest-zfn-docker/Tutorial/worlds/Tutorial  /opt/minetest-zfn-docker/worlds
echo "Tutorial starten: ./startWorld.sh Tutorial"

