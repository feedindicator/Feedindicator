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

"""A RSS feed reader for the indicator area."""


import os.path


__author__ = 'Nathanael Philipp'
__copyright__ = 'Copyright 2017 Nathanael Philipp (jnphilipp)'
__license__ = 'GPLv3'
__maintainer__ = __author__
__email__ = 'mail@jnphilipp.org'
__app_name__ = 'feedindicator'
__version_info__ = (2, 0, 0)
__version__ = '.'.join(str(e) for e in __version_info__)
__description__ = 'A RSS feed reader for the indicator area.'
__github__ = 'https://github.com/jnphilipp/Feedindicator'

basedir = os.path.dirname(os.path.realpath(__file__))
