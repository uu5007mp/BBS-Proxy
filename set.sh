#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

install_debian() {
    if ! dpkg -s "$1" &> /dev/null; then
        if ! apt install -y "$1"; then
            echo "Failed to install $1 on Debian-based system"
            exit 1
        fi
    fi
}

install_arch() {
    if ! pacman -Qi "$1" &> /dev/null; then
        if ! pacman -S --noconfirm "$1"; then
            echo "Failed to install $1 on Arch-based system"
            exit 1
        fi
    fi
}

install_redhat() {
    if ! rpm -q "$1" &> /dev/null; then
        if ! yum install -y "$1"; then
            echo "Failed to install $1 on RedHat-based system"
            exit 1
        fi
    fi
}

install_packages() {
    installer=$1
    shift
    for package in "$@"; do
        $installer "$package"
    done
}

if [ -f /etc/debian_version ]; then
    if ! apt update; then
        echo "Failed to update package list on Debian-based system"
        exit 1
    fi
    install_packages install_debian git npm
elif [ -f /etc/arch-release ]; then
    if ! pacman -Syu --noconfirm; then
        echo "Failed to update package list on Arch-based system"
        exit 1
    fi
    install_packages install_arch git npm
elif [ -f /etc/redhat-release ]; then
    if ! yum update -y; then
        echo "Failed to update package list on RedHat-based system"
        exit 1
    fi
    install_packages install_redhat git npm
else
    echo "Unsupported distribution"
    exit 1
fi

if ! git clone https://github.com/uu5007mp/BBS-Proxy.git; then
    echo "Failed to clone the repository"
    exit 1
fi

cd BBS-Proxy || { echo "Failed to change directory to BBS-Proxy"; exit 1; }

if ! npm install; then
    echo "Failed to install npm dependencies"
    exit 1
fi

if ! npm start; then
    echo "Failed to start the application"
    exit 1
fi
