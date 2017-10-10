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

from math import ceil, floor


def app_version():
    """Generate command line version text."""
    def line(text):
        """Make single line with padding left and right."""
        return '#%s%s%s#\n' % (' ' * floor((47 - len(text)) / 2),
                               text,
                               ' ' * ceil((47 - len(text)) / 2))

    return (('#################################################\n' +
             line(feedindicator.__app_name__) +
             line(feedindicator.__description__) +
             line('') +
             line(feedindicator.__version__) +
             line(feedindicator.__license__) +
             line(feedindicator.__author__) +
             line(feedindicator.__email__) +
             line('') +
             line(feedindicator.__github__) +
             '#################################################'))
