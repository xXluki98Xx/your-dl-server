#!/usr/bin/env bash

oPath="$PWD"

cd ..

pip3 install -r requirements.txt --upgrade
cat requirements-apt.txt | xargs sudo apt install -y

cd your-dl-server

if [ -f ~/.zshrc ]; then
    echo '

# dl.py from ServerScripts
export PATH="'$PWD:\$PATH'"' >> ~/.zshrc

fi

cd $oPath