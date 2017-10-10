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
import gettext
import gi
gi.require_version('Gtk', '3.0')
import os

from feedindicator import config, feeds
from feedindicator.utils import autostart, SQLite
from gi.repository import Gtk, Gdk


class PreferencesDialog(Gtk.Window):
    """Preferences dialog.

    Attributes:
        _configs: dict with configs
        _config_manager: config manager
        _callback: callback function after url has been added
        _callback_args: arguments for callback function
        _feeds: list store for the feeds with id, title, feed_url
        _treeview: treeview for the feeds
        _btn_remove_feed: remove button for feeds
        _refreshtime_label: label for refresh time config
        _scaletime: scaler for refresh time config
        _items_per_feed_label: label for items per feed config
        _btn_show_update_notifications: check button for show update
                notifications config
    """
    def __init__(self, widget, config_manager, callback, *args):
        """Init dialog.

        Args:
            widget: Gtk widget
            configs: dict with configs
            callback: callback function after url has been added
            *args: callback function args
        """
        Gtk.Window.__init__(self, title=_('Preferences'))
        self._config_manager = config_manager
        self._configs = self._config_manager.items()
        self._callback = callback
        self._callback_args = args

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_icon_name(feedindicator.__app_name__)
        self.connect('delete_event', self._close_window)
        self.connect('key-press-event', self._keypress)

        vbox = Gtk.VBox(False, 1)
        vbox.set_border_width(1)
        self.add(vbox)

        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        vbox.pack_start(notebook, False, True, 0)

        # Feed List
        frame = Gtk.Frame(label=_('Feed list'))
        frame.set_border_width(1)

        box = Gtk.VBox(False, 1)
        box.set_border_width(1)
        frame.add(box)

        label = Gtk.Label(label=_('Configure the feeds.'))
        label.set_justify(Gtk.Justification.LEFT)
        label.set_line_wrap(True)
        box.pack_start(label, False, True, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC,
                                   Gtk.PolicyType.ALWAYS)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.set_min_content_height(500)
        scrolled_window.set_min_content_width(500)
        box.pack_start(scrolled_window, False, True, 0)

        self._feeds = Gtk.ListStore(int, str, str)
        with SQLite() as db:
            for feed in db.s('SELECT id, title, feed_url FROM feeds ORDER ' +
                             'BY UPPER(title)'):
                self._feeds.append(feed)

        self._treeview = Gtk.TreeView.new_with_model(self._feeds)
        for i, column_title in enumerate([_('ID'), _('Title'), _('URL')]):
            renderer = Gtk.CellRendererText()
            if i > 0:
                renderer.set_property('editable', True)
                renderer.connect('edited', self._cell_edited, i)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self._treeview.append_column(column)

        self._treeview.set_headers_clickable(False)
        self._treeview.set_reorderable(True)
        self._treeview.connect('cursor-changed', self._selection_made)
        scrolled_window.add(self._treeview)

        hbox = Gtk.HBox(True, 1)
        box.pack_start(hbox, False, True, 0)

        btn = Gtk.Button(label=_('Add'))
        btn.connect('clicked', self._add_feed)
        hbox.pack_start(btn, False, True, 0)

        self._btn_remove_feed = Gtk.Button(label=_('Remove'))
        self._btn_remove_feed.connect('clicked', self._remove_feed)
        self._btn_remove_feed.set_sensitive(False)
        hbox.pack_start(self._btn_remove_feed, False, True, 0)
        notebook.append_page(frame, Gtk.Label(label=_('Feed list')))

        # Options
        frame = Gtk.Frame(label=_('Options'))
        frame.set_border_width(1)

        box = Gtk.VBox(False, 1)
        box.set_border_width(1)
        frame.add(box)

        btn = Gtk.CheckButton(label=_('Auto update feeds'))
        btn.set_active(not self._configs['stoptimer'])
        btn.connect('toggled', self._toggle_config, 'stoptimer')
        box.pack_start(btn, False, True, 0)

        hbox = Gtk.HBox(True, 0)
        box.pack_start(hbox, False, True, 0)

        self._refreshtime_label = Gtk.Label(label='')
        hbox.pack_start(self._refreshtime_label, False, True, 0)

        adjtimer = Gtk.Adjustment(value=self._configs['refreshtime'] / 60,
                                  lower=1.0, upper=90.0, step_increment=1.0,
                                  page_increment=10.0, page_size=0.0)
        adjtimer.connect('value_changed', self._change_refreshtime)
        self._scaletime = Gtk.HScale(adjustment=adjtimer)
        self._scaletime.set_draw_value(False)
        self._scaletime.set_digits(0)
        self._scaletime.set_sensitive(not self._configs['stoptimer'])
        hbox.pack_start(self._scaletime, False, True, 0)
        self._change_refreshtime(adjtimer)

        hbox = Gtk.HBox(True, 0)
        box.pack_start(hbox, False, True, 0)

        self._items_per_feed_label = Gtk.Label(label='')
        hbox.pack_start(self._items_per_feed_label, False, False, 0)

        adjitems = Gtk.Adjustment(value=self._configs['items_per_feed'],
                                  lower=1.0, upper=30.0, step_increment=1.0,
                                  page_increment=10.0, page_size=0.0)
        adjitems.connect('value_changed', self._change_items_per_feed)
        scaleitems = Gtk.HScale(adjustment=adjitems)
        scaleitems.set_draw_value(False)
        scaleitems.set_digits(0)
        hbox.pack_start(scaleitems, True, True, 0)
        self._change_items_per_feed(adjitems)

        btn = Gtk.CheckButton(label=_('Show feeds at top of menu'))
        btn.set_active(self._configs['feeds_at_top'])
        btn.connect('toggled', self._toggle_config, 'feeds_at_top')
        box.pack_start(btn, False, True, 0)

        btn = Gtk.CheckButton(label=_('Show feeds with no unread posts'))
        btn.set_active(self._configs['show_unread_feeds'])
        btn.connect('toggled', self._toggle_config, 'show_unread_feeds')
        box.pack_start(btn, False, True, 0)

        btn = Gtk.CheckButton(label=_('Launch at system startup'))
        btn.set_active(self._configs['autostart'])
        btn.connect('toggled', self._toggle_config, 'autostart')
        box.pack_start(btn, False, True, 0)

        btn = Gtk.CheckButton(label=_('Show notifications'))
        btn.set_active(self._configs['show_notifications'])
        btn.connect('toggled', self._toggle_config, 'show_notifications')
        box.pack_start(btn, False, True, 0)

        self._btn_show_update_notifications = Gtk. \
            CheckButton(label=_('Show notifications at beginning ' +
                                'and end of update'))
        self._btn_show_update_notifications. \
            set_sensitive(self._configs['show_notifications'])
        self._btn_show_update_notifications. \
            set_active(self._configs['show_update_notifications'])
        self._btn_show_update_notifications. \
            connect('toggled', self._toggle_config,
                    'show_update_notifications')
        box.pack_start(self._btn_show_update_notifications, False, True, 0)

        notebook.append_page(frame, Gtk.Label(label=_('Options')))

        box = Gtk.HBox(True, 0)
        vbox.pack_end(box, False, True, 0)

        btn = Gtk.Button(label=_('Cancel'))
        btn.connect('clicked', self._close_window)
        box.pack_start(btn, False, True, 0)

        btn = Gtk.Button(label=_('Save'))
        btn.connect('clicked', self._save)
        box.pack_start(btn, False, True, 0)
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
        """Save config and feeds and close dialog.

        Args:
            widget: Gtk widget
        """
        self._config_manager.update(self._configs)
        self._config_manager.save()
        with SQLite() as db:
            for feed in self._feeds:
                if feed[0] == -1 and feed[2]:
                    if not feed[1]:
                        feed[1] = None
                    db.s('INSERT INTO feeds (feed_url, title) VALUES (?,?)',
                         (feed[2], feed[1]))
                else:
                    db.s('UPDATE feeds set title=?, feed_url=? WHERE id=?',
                         (feed[1], feed[2], feed[0]))
        self._close_window(widget)
        self._callback(self._callback_args)

    def _selection_made(self, widget):
        """Feed selected from list, so we enable the remove button.

        Args:
            widget: Gtk widget
        """
        sel = self._treeview.get_selection().get_selected()
        if sel[1] is not None:
            self._btn_remove_feed.set_sensitive(True)

    def _cell_edited(self, widget, path, text, column):
        """Update list store after cell has been edited.

        Args:
            widget: Gtk widget
            path: row id
            text: new text
            column: column id
        """
        self._feeds[path][column] = text

    def _add_feed(self, widget):
        """Add a row to list.

        Args:
            widget: Gtk widget
        """
        sel = self._feeds.append([-1, '', ''])
        pos = self._feeds.get_path(sel)
        self._treeview.set_cursor(pos, None, False)

    def _remove_feed(self, widget):
        """Remove selected feed from list and delete from database.

        Args:
            widget: Gtk widget
        """
        sel = self._treeview.get_selection().get_selected()
        feed_id = sel[0].get_value(sel[1], 0)
        if feed_id != -1:
            feeds.delete(feed_id)
        self._feeds.remove(sel[1])
        self._treeview.get_selection().unselect_all()
        self._btn_remove_feed.set_sensitive(False)

    def _change_refreshtime(self, widget):
        """Change refresh time.

        Args:
            widget: Gtk widget
        """
        value = widget.get_value()
        self._configs['refreshtime'] = int(value * 60)
        text = gettext.ngettext('Update feeds every minute',
                                'Update feeds every %(minutes)d minutes',
                                value) % {'minutes': value}
        self._refreshtime_label.set_text(text)

    def _change_items_per_feed(self, widget):
        """Change items per feed.

        Args:
            widget: Gtk widget
        """
        value = widget.get_value()
        self._configs['items_per_feed'] = int(value)
        text = gettext.ngettext('Show 1 item per feed',
                                'Show %(items)d items per feed',
                                value) % {'items': value}
        self._items_per_feed_label.set_text(text)

    def _toggle_config(self, widget, key):
        """Toggles config values.

        Args:
            widget: Gtk widget
            key: config key
        """
        self._configs[key] = widget.get_active()
        if key == 'autostart':
            if self._configs[key]:
                autostart.create()
            else:
                autostart.delete()
        elif key == 'stoptimer':
            if self._configs[key]:
                self._scaletime.set_sensitive(True)
            else:
                self._scaletime.set_sensitive(False)
