#/bin/bash
read -p "Dieses Script setzt die Tutorial-Welt zurück. Bist du sicher? Mit 'J' bestätigen!" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Jj]$ ]]
then
    read -p "Bist du wirklich, wirklich sicher? Dann mit Y bestätigen." -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
	ls
    fi
fi
