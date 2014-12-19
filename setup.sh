#!/usr/bin/env bash
set -e

ask() {
  # http://djm.me/ask
  while true; do

    if [ "${2:-}" = "Y" ]; then
      prompt="Y/n"
      default=Y
    elif [ "${2:-}" = "N" ]; then
      prompt="y/N"
      default=N
    else
      prompt="y/n"
      default=
    fi

    # Ask the question
    read -p "$1 [$prompt] " REPLY

    # Default?
    if [ -z "$REPLY" ]; then
       REPLY=$default
    fi

    # Check if the reply is valid
    case "$REPLY" in
      Y*|y*) return 0 ;;
      N*|n*) return 1 ;;
    esac

  done
}

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

ask "Install packages?" Y && {
  sudo apt-get install -y ${DEPS_GENERAL}
  sudo apt-get install -y ${DEPS_I3}
  sudo apt-get install -y ${DEPS_COMPTON}
}

ask "Install python3 modules?" Y && { sudo pip3 install ${DEPS_PYTHON3} }

dir=`pwd`
if [ ! -e "${dir}/${0}" ]; then
  echo "Script not called from within repository directory. Aborting."
  exit 2
fi

ask "Install symlink for .gitconfig?" Y && ln -sfn ${dir}/.gitconfig ${HOME}/.gitconfig
ask "Install symlink for .conkyrc?" Y && ln -sfn ${dir}/.conkyrc ${HOME}/.conkyrc
ask "Install symlink for .bashrc?" Y && ln -sfn ${dir}/.bashrc ${HOME}/.bashrc
ask "Install symlink for .vimrc?" Y && ln -sfn ${dir}/.vimrc ${HOME}/.vimrc
ask "Install symlink for .Xresources?" Y && ln -sfn ${dir}/.Xresources ${HOME}/.Xresources
ask "Install symlink for .compton.conf?" Y && ln -sfn ${dir}/.compton.conf ${HOME}/.compton.conf

ask "Install symlink for .i3/?" Y && ln -sfn ${dir}/.i3 ${HOME}/.i3
ask "Install symlink for .vim/?" Y && ln -sfn ${dir}/.vim ${HOME}/.vim
ask "Install symlink for .bash.d/?" Y && ln -sfn ${dir}/.bash.d ${HOME}/.bash.d

ask "Install symlink for scripts/?" Y && ln -sfn ${dir}/scripts ${HOME}/scripts

ask "Install hard link for /etc/sudoers.d/power-control?" Y && sudo ln ${dir}/etc/sudoers.d/power-control /etc/sudoers.d/power-control
