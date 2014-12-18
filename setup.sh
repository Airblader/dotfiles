#!/usr/bin/env bash
set -e

distro=`lsb_release -si`
if [ "${distro}" != "Ubuntu" ]; then
  echo "Distro is not Ubuntu, packages may not apply. Aborting."
  exit 2
fi

DEPS_GENERAL="conky i3lock suckless-tools iwlib python3 python3-pip gnome-settings-daemon nm-applet acpi xdotool scrot feh \
amixer pacmd pactl nautilus"

DEPS_I3="libxcb1-dev libxcb-keysyms1-dev libpango1.0-dev libxcb-util0-dev libxcb-icccm4-dev \
libyajl-dev libstartup-notification0-dev libxcb-randr0-dev libev-dev libxcb-cursor-dev libxcb-xinerama0-dev \
libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev"

DEPS_COMPTON="libglu1-mesa-dev libdbus-1-dev libxcomposite-dev libxdamage-dev \
libxfixes-dev libxext-dev libxrender-dev libxrandr-dev libxinerama-dev pkg-config \
x11-utils libpcre3-dev libconfig-dev libdrm-dev asciidoc"

DEPS_PYTHON3="basiciw netifaces jsonpath_rw"

`sudo apt-get install ${DEPS_GENERAL}`
`sudo apt-get install ${DEPS_I3}`
`sudo apt-get install ${DEPS_COMPTON}`

`sudo pip3 install ${DEPS_PYTHON3}`
