#!/bin/sh
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install python python-imaging python-opencv python-numpy
sudo apt-get install git-core
sudo apt-get install arduino
sudo apt-get install minicom

git config --global user.name "Trevor Stanhope"
git config --global user.email "tpstanhope@gmail.com"

sudo mv /etc/network/interfaces /etc/network/interfaces.backup
sudo cp config/interfaces /etc/network/
sudo mv /etc/hosts /etc/hosts.backup
sudo cp config/hosts /etc
