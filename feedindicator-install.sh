#!/bin/sh

sudo apt-get install python-feedparser
sudo xdg-icon-resource install --theme ubuntu-mono-dark --novendor --size 22 dark/indicator-feedindicator.png indicator-feedindicator
sudo xdg-icon-resource install --theme ubuntu-mono-dark --novendor --size 22 dark/indicator-feedindicator-attention.png indicator-feedindicator-attention
sudo xdg-icon-resource install --theme ubuntu-mono-light --novendor --size 22 light/indicator-feedindicator.png indicator-feedindicator
sudo xdg-icon-resource install --theme ubuntu-mono-light --novendor --size 22 light/indicator-feedindicator-attention.png indicator-feedindicator-attention
sudo xdg-icon-resource install --theme hicolor --novendor --size 22 hicolor/indicator-feedindicator.png indicator-feedindicator
sudo xdg-icon-resource install --theme hicolor --novendor --size 22 hicolor/indicator-feedindicator-attention.png indicator-feedindicator-attention
sudo xdg-icon-resource install --theme hicolor --novendor --size 128 --context apps feedindicator-logo.png feedindicator
sudo xdg-icon-resource install --theme hicolor --novendor --size 48 --context apps feedindicator-48x48.png feedindicator

sudo xdg-desktop-menu install --novendor feedindicator.desktop

if [ ! -d /usr/share/feedindicator/ ]
then
sudo mkdir /usr/share/feedindicator
fi

sudo cp feedindicator-icon.png /usr/share/feedindicator/feedindicator-icon.png
sudo cp feedindicator-logo.png /usr/share/feedindicator/feedindicator-logo.png

sudo cp feedindicator /usr/bin/feedindicator
sudo chmod +x /usr/bin/feedindicator

MESSAGE="Feedindicator install completed."
echo $MESSAGE

