#!/usr/bin/env bash

oPath="$PWD"

cd ..

echo "install requiremtents"
pip3 install -r requirements.txt --upgrade
sudo apt update
cat requirements-apt.txt | sed $'s/\r$//g' | xargs sudo apt install -y


cd your-dl-server

echo "generate unix"
sed $'s/\r$//' ./dl.py > ./dl.unix.py


echo "add to shell"
if [ -f ~/.zshrc ]; then
    echo '

# dl.py from your-dl-server
export PATH="'$PWD:\$PATH'"' >> ~/.zshrc

elif [ -f ~/.bashrc ]; then
    echo '

# dl.py from your-dl-server
export PATH="'$PWD:\$PATH'"' >> ~/.bashrc

else

    echo 'export PATH="'$PWD:\$PATH'"'

fi

echo "finished"

cd $oPath