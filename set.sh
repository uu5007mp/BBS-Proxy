#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

install_debian() {
    dpkg -s "$1" &> /dev/null || apt install -y "$1"
}

install_arch() {
    pacman -Qi "$1" &> /dev/null || pacman -S --noconfirm "$1"
}

install_redhat() {
    rpm -q "$1" &> /dev/null || yum install -y "$1"
}

install_packages() {
    for package in "$@"; do
        $1 "$package"
    done
}

if [ -f /etc/debian_version ]; then
    apt update
    install_packages install_debian git npm
elif [ -f /etc/arch-release ]; then
    pacman -Syu --noconfirm
    install_packages install_arch git npm
elif [ -f /etc/redhat-release ]; then
    yum update -y
    install_packages install_redhat git npm
else
    echo "Unsupported distribution"
    exit 1
fi

git clone https://github.com/uu5007mp/BBS-Proxy.git
cd BBS-Proxy
npm install
npm start
