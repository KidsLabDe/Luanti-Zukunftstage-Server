#!/bin/bash
# cd /opt/minetest
cp main-config/tutorial.conf main-config/minetest.conf
docker-compose -f tutorial.yaml stop
rm debug.txt
#rm -R /opt/minetest-zfn-docker/worlds/Tutorial
#cp -R /opt/minetest-zfn-docker/Tutorial/worlds/Tutorial  /opt/minetest-zfn-docker/worlds
docker-compose -f tutorial.yaml up

