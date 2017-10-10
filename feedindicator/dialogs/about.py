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
import gi
gi.require_version('Gtk', '3.0')

from feedindicator import config
from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):
    """About dialog."""
    def __init__(self, widget):
        """Init dialog.

        Args:
            widget: Gtk widget
        """
        Gtk.AboutDialog.__init__(self, _('About'))
        self.set_icon_name(feedindicator.__app_name__)
        self.set_logo(Gtk.IconTheme.get_default(). \
            load_icon(feedindicator.__app_name__, 128, 0))
        self.set_name(feedindicator.__app_name__)
        self.set_program_name(feedindicator.__app_name__)
        self.set_version(feedindicator.__version__)
        self.set_comments(feedindicator.__description__)
        self.set_copyright(feedindicator.__copyright__)
        self.set_license(feedindicator.__license__)
        self.set_website(feedindicator.__github__)
        self.set_website_label(feedindicator.__github__)
        self.set_authors(feedindicator.__author__.split(', '))
        self.run()
        self.destroy()
