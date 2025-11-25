#!/bin/bash
#cd /opt/minetest
read -p "Dieses Script setzt die Tutorial-Welt zurück. Bist du sicher? Mit 'J' bestätigen!" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Jj]$ ]]
then
    read -p "Bist du wirklich, wirklich sicher? Dann mit Y bestätigen." -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        cp main-config/tutorial.conf main-config/minetest.conf
        docker-compose -f tutorial.yaml stop
        rm debug.txt
        rm -R worlds/Tutorial
        cp -R minetest-Tutorial/worlds/Tutorial  worlds/
    fi
fi

# docker-compose -f tutorial.yaml up
echo "Zurückgesetzt. Enter zum schließen."
read
