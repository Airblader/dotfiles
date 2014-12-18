#!/usr/bin/env bash
set -e

distro=`lsb_release -si`
if [ "${distro}" != "Ubuntu" ]; then
  echo "Distro is not Ubuntu, packages may not apply. Aborting."
  exit 2
fi

DEPS_GENERAL="conky i3lock suckless-tools libiw-dev python3 python3-pip gnome-settings-daemon acpi xdotool scrot feh dconf-editor \
rxvt-unicode-256color"

DEPS_I3="libxcb1-dev libxcb-keysyms1-dev libpango1.0-dev libxcb-util0-dev libxcb-icccm4-dev \
libyajl-dev libstartup-notification0-dev libxcb-randr0-dev libev-dev libxcb-cursor-dev libxcb-xinerama0-dev \
libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev"

DEPS_COMPTON="libglu1-mesa-dev libdbus-1-dev libxcomposite-dev libxdamage-dev \
libxfixes-dev libxext-dev libxrender-dev libxrandr-dev libxinerama-dev pkg-config \
x11-utils libpcre3-dev libconfig-dev libdrm-dev asciidoc"

DEPS_PYTHON3="basiciw netifaces jsonpath_rw"

sudo apt-get install -y ${DEPS_GENERAL}
sudo apt-get install -y ${DEPS_I3}
sudo apt-get install -y ${DEPS_COMPTON}

sudo pip3 install ${DEPS_PYTHON3}

dir=`pwd`
if [ ! -e "${dir}/${0}" ]; then
  echo "Script not called from within repository directory. Aborting."
  exit 2
fi

# TODO ask for everything
ln -sfn ${dir}/.gitconfig ${HOME}/.gitconfig
ln -sfn ${dir}/.conkyrc ${HOME}/.conkyrc
ln -sfn ${dir}/.bashrc ${HOME}/.bashrc
ln -sfn ${dir}/.vimrc ${HOME}/.vimrc
ln -sfn ${dir}/.Xresources ${HOME}/.Xresources
ln -sfn ${dir}/.compton.conf ${HOME}/.compton.conf

ln -sfn ${dir}/.i3 ${HOME}/.i3
ln -sfn ${dir}/.vim ${HOME}/.vim
ln -sfn ${dir}/.bash.d ${HOME}/.bash.d

ln -sfn ${dir}/scripts ${HOME}/scripts

sudo cp ${dir}/etc/sudoers.d/power-control /etc/sudoers.d/
