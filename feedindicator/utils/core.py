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


import hashlib


def get_hash(*args):
    """Calculate hash for combined string of arguments.

    Args:
        args: values to hash
    """
    return hashlib.sha512('@'.join(a for a in args if a). \
        encode('utf-8')).hexdigest()
