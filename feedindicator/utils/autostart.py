# -*- coding: utf-8 -*-

# Copyright (C) 2010-2017 Dave Gardner <eunbolt@gmail.com>,
#                         Michael Judge <email@clickopen.co.uk>,
#                         Nicolas Raoul <nicolas.raoul@gmail.com>,
#                         Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
#
# This file is part of feedindicator.
#
# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# feedindicator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with feedindicator.  If not, see <http://www.gnu.org/licenses/>.


import feedindicator
import os

from feedindicator import config


def create():
    """Create autostart file."""
    if not os.path.exists(config.app_autostart_dir):
        os.makedirs(config.app_autostart_dir, 0o700)
    with open(config.app_autostart_file, 'w', encoding='utf-8') as f:
        f.write('[Desktop Entry]\n')
        f.write('Type=Application\n')
        f.write('Exec=%s --autostarted\n' % feedindicator.__app_name__)
        f.write('X-GNOME-Autostart-enabled=true\n')
        f.write('Icon=%s\n' % feedindicator.__app_name__)
        f.write('Name=%s\n' % feedindicator.__app_name__)
        f.write('Comment=%s' % feedindicator.__description__)


def delete():
    """Delete autostart file."""
    if os.path.exists(config.app_autostart_file):
        os.remove(config.app_autostart_file)
