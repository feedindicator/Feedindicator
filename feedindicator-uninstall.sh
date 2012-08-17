#!/bin/sh

sudo xdg-icon-resource uninstall --theme ubuntu-mono-dark --size 22 indicator-feedindicator
sudo xdg-icon-resource uninstall --theme ubuntu-mono-dark --size 22 indicator-feedindicator-attention
sudo xdg-icon-resource uninstall --theme ubuntu-mono-light --size 22 indicator-feedindicator
sudo xdg-icon-resource uninstall --theme ubuntu-mono-light --size 22 indicator-feedindicator-attention
sudo xdg-icon-resource uninstall --theme hicolor --size 22 indicator-feedindicator
sudo xdg-icon-resource uninstall --theme hicolor --size 22 indicator-feedindicator-attention
sudo xdg-icon-resource uninstall --theme hicolor --size 128 --context apps feedindicator
sudo xdg-icon-resource uninstall --theme hicolor --size 48 --context apps feedindicator

sudo xdg-desktop-menu uninstall feedindicator.desktop

sudo unlink /usr/bin/feedindicator

sudo unlink /usr/share/feedindicator/feedindicator-icon.png
sudo unlink /usr/share/feedindicator/feedindicator-logo.png

sudo rmdir /usr/share/feedindicator

[ ! "$XDG_CACHE_HOME" ] && XDG_CACHE_HOME=~/.cache
cachedir="$XDG_CACHE_HOME"/feedindicator
[ ! "$XDG_CONFIG_HOME" ] && XDG_CONFIG_HOME=~/.config
configdir="$XDG_CONFIG_HOME"/feedindicator
autostartfile="$XDG_CONFIG_HOME"/autostart/feedindicator.desktop

if [ -f "$autostartfile" ]
then
unlink "$autostartfile"
fi

if [ -d "$configdir" ]
then
rm -r "$configdir"
fi

if [ -d "$cachedir" ]
then
rm -r "$cachedir"
fi

MESSAGE="Feedindicator uninstall completed."
echo $MESSAGE

