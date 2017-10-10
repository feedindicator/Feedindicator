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

from gi.repository import GLib


# indicator icon names
active_icon = 'feedindicator-active'
attention_icon = 'feedindicator-attention'

# XDG config
xdg_config_dir = GLib.get_user_config_dir()
app_config_dir = os.path.join(xdg_config_dir, feedindicator.__app_name__)
app_autostart_dir = os.path.join(xdg_config_dir, 'autostart')
app_autostart_file = os.path.join(app_autostart_dir,
                                  '%s.desktop' % feedindicator.__app_name__)

# XDG cache
xdg_cache_dir = GLib.get_user_cache_dir()
app_cache_dir = os.path.join(xdg_cache_dir, feedindicator.__app_name__)

# XDG data
xdg_data_dir = GLib.get_user_data_dir()
app_data_dir = os.path.join(xdg_data_dir, feedindicator.__app_name__)
app_database = os.path.join(app_data_dir, 'db.sqlite3')

# # /usr/share/
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_locale_dir = os.path.join(base_dir, 'locale')
