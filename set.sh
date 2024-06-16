#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

check_and_install() {
    dpkg -s $1 &> /dev/null
    if [ $? -ne 0 ]; then
        apt install -y $1
    fi
}

apt update

check_and_install git
check_and_install npm

git clone https://github.com/hirotomoki12345/Ultraviolet-App.git

cd Ultraviolet-App

npm install
npm start
