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
import sqlite3
import sys

from feedindicator import feeds
from gi.repository import Gtk, Gdk


class AddFeedDialog(Gtk.Window):
    """Dialog to add a new feed url.

    Attributes:
        _callback: callback function after url has been added
        _callback_args: arguments for callback function
        _textbox: textbox for feed url
    """
    def __init__(self, widget, callback, *args):
        """Init dialog.

        Args:
            widget: Gtk widget
            callback: callback function after url has been added
            args: arguments for callback function
        """
        Gtk.Window.__init__(self, title=_('Add feed'))
        self._callback = callback
        self._callback_args = args

        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name(feedindicator.__app_name__)
        self.connect('delete_event', self._close_window)
        self.connect('key-press-event', self._keypress)

        vbox = Gtk.VBox(False, 10)
        vbox.set_border_width(10)
        self.add(vbox)

        box = Gtk.HBox(False, 0)
        vbox.pack_start(box, False, True, 0)

        label = Gtk.Label(label=_('Feed url'))
        label.set_justify(Gtk.Justification.LEFT)
        label.set_line_wrap(True)
        box.pack_start(label, False, True, 0)

        box = Gtk.HBox(False, 0)
        vbox.pack_start(box, False, True, 0)

        self._textbox = Gtk.Entry()
        box.pack_start(self._textbox, True, True, 0)
        self._textbox.connect("activate", self._save)

        box = Gtk.HBox(True, 0)
        vbox.pack_end(box, False, True, 5)

        button = Gtk.Button(_('Cancel'))
        box.pack_start(button, True, True, 0)
        button.connect('clicked', self._close_window)
        button = Gtk.Button(_('Add feed'))
        box.pack_start(button, True, True, 0)
        button.connect('clicked', self._save)

        self.set_keep_above(True)
        self.show_all()

    def _keypress(self, widget, data):
        """Keypress handler.

        Args:
            widget: Gtk widget
            data: key event data
        """
        if data.keyval == Gdk.KEY_Escape:
            self._close_window(widget)

    def _close_window(self, widget, data=None):
        """Close dialog.

        Args:
            widget: Gtk widget
            data: optional key event data
        """
        self.close()

    def _save(self, widget):
        """Save feed and close dialog.

        Args:
            widget: Gtk widget
        """
        self.set_modal(True)
        try:
            if self._textbox.get_text():
                feeds.add(self._textbox.get_text())
            self._close_window(widget)
            if self._callback:
                self._callback(self._callback_args)
        except sqlite3.Error as e:
            print('Could not add feed.', e, file=sys.stderr)
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CANCEL,
                                       _('Could not add feed.'))
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
