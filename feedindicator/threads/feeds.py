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


from feedindicator import feeds
from gi.repository import GLib
from threading import Thread


class FeedThread(Thread):
    """Feed thread, to run feed updates in a separate thread.

    Attributes:
        _callback: callback function after url has been added
        _callback_args: arguments for callback function
    """
    def __init__(self, callback, *args):
        """Init feed thread.

        Args:
            callback: callback function after url has been added
            args: arguments for callback function
        """
        Thread.__init__(self, name='FeedThread')
        self._callback = callback
        self._callback_args = args

    def run(self):
        """Updates all feeds in the database und updates the infos"""
        feeds.update()
        GLib.idle_add(self._callback, self._callback_args)
