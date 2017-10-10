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


import os

from configparser import RawConfigParser
from feedindicator.config.constants import app_config_dir


class ConfigManager:
    """Configuration manager. All configurations can either be acces through
        key words or per '.'.

    Attributes:
        _configs: configuration dict
    """
    def __init__(self):
        """"Init config manager with default configurations."""
        self.__dict__['_configs'] = {# defaults
            'autostart': False,
            'refreshtime': 30 * 60,
            'stoptimer': False,
            'items_per_feed': 10,
            'show_notifications': True,
            'show_update_notifications': True,
            'feeds_at_top': False,
            'show_unread_feeds': True
        }

    def __getattr__(self, key):
        return self.__dict__['_configs'][key]

    def __setattr__(self, key, val):
        if key in self.__dict__['_configs']:
            self.__dict__['_configs'][key] = val
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        return self._configs[key]

    def __setitem__(self, key, val):
        if key in self._configs:
            self._configs[key] = val
        else:
            raise KeyError(key)

    def items(self):
        """Get all configurations."""
        return dict((k, v) for k, v in self._configs.items())

    def update(self, updates):
        """Update configurations with given dict."""
        for k, v in updates.items():
            self._configs[k] = v

    def keys(self):
        """Get all configuration names."""
        return self._configs.keys()

    def load(self):
        """Load configurations from file."""
        parser = RawConfigParser()
        parser.optionxform = str
        parser.read(os.path.join(app_config_dir, 'config'))
        if parser.has_option('Options', 'autostart'):
            self.autostart = parser.getboolean('Options', 'autostart')
        if parser.has_option('Options', 'refreshtime'):
            self.refreshtime = parser.getint('Options', 'refreshtime')
        if parser.has_option('Options', 'stoptimer'):
            self.stoptimer = parser.getboolean('Options', 'stoptimer')
        if parser.has_option('Options', 'items_per_feed'):
            self.items_per_feed = parser.getint('Options', 'items_per_feed')
        if parser.has_option('Options', 'show_notifications'):
            self.show_notifications = parser.getboolean('Options',
                                                        'show_notifications')
        if parser.has_option('Options', 'show_update_notifications'):
            self.show_update_notifications = parser. \
                getboolean('Options', 'show_update_notifications')
        if parser.has_option('Options', 'feeds_at_top'):
            self.feeds_at_top = parser.getboolean('Options', 'feeds_at_top')
        if parser.has_option('Options', 'show_unread_feeds'):
            self.show_unread_feeds = parser.getboolean('Options',
                                                       'show_unread_feeds')

    def save(self):
        """Save configuration to file."""
        parser = RawConfigParser()
        parser.optionxform = str
        parser.read_dict({'Options': self._configs})
        with open(os.path.join(app_config_dir, 'config'), 'w',
                  encoding='utf-8') as f:
            parser.write(f)
