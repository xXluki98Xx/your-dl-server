#!/usr/bin/env bash

oPath="$PWD"

pip3 install -r requirements.txt --upgrade
cat requirements-apt.txt | xargs sudo apt install -y

cd ..

echo '

# dl.py from ServerScripts
export PATH="'$PWD:\$PATH'"' >> ~/.dotfiles/zsh/zshrc

cd $oPath