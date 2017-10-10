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
import sys
import webbrowser

from feedindicator import config, feeds
from feedindicator.dialogs import AboutDialog, AddFeedDialog, PreferencesDialog
from feedindicator.threads import FeedThread
from feedindicator.utils import SQLite
from gi.repository import GLib, Gtk, Notify
from time import sleep, time

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as appindicator
except (ImportError, ValueError):
    appindicator = None


class AppIndicator:
    """App indicator.

    Attributes:
        _config_manager: config manager
        _feeds_thread: feeds thread
        _indicator: app indicator
        _status_icon: Gtk status icon, if app indicator isn't available
        _menu: menu
    """
    def __init__(self, config_manager):
        """Init indicator.

        Args:
            config_manager: config manager
        """
        self._config_manager = config_manager
        self._feeds_thread = None

        if appindicator:
            # Create indicator
            self._indicator = appindicator.Indicator. \
                new(feedindicator.__app_name__, feedindicator.__app_name__,
                    appindicator.IndicatorCategory.APPLICATION_STATUS)
            self._indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
            self._indicator.set_attention_icon_full(config.attention_icon,
                                                    _('New Posts.'))
            self._indicator.set_icon_full(config.active_icon,
                                          _('Nothing new.'))
        else:
            # Create status icon
            self._status_icon = Gtk.StatusIcon()
            self._status_icon.set_name(feedindicator.__app_name__)
            self._status_icon.set_from_icon_name(config.active_icon)
            self._status_icon.set_tooltip_text(feedindicator.__app_name__)

        # Create popup menu
        self._menu = Gtk.Menu()
        if appindicator:
            self._menu.show_all()
            self._indicator.set_menu(self._menu)
        else:
            self._status_icon.connect('activate', self._toggle_status_icon)
            self._status_icon.connect('popup-menu', self._popup_menu)
            self._status_icon.set_visible(True)

        self._update(None, True, True)

    def _popup_menu(self, widget, button, time):
        """Callback when the popup menu on the status icon has to open.

        Args:
            widget: Gtk widget
            button: mouse button
            time: activation time
        """
        self._menu.show_all()
        self._menu.popup(None, None, Gtk.StatusIcon.position_menu,
                         self._status_icon, button, time)

    def _toggle_status_icon(self, widget):
        """Callback when a request to toggle feedindicator was made.

        Args:
            widget: Gtk widget
        """
        self._popup_menu(widget, 0, Gtk.get_current_event_time())

    def _set_status(self, status):
        """Turns the appindicator to attention and back to normal.

        Args:
            status: new indicator status: attention/active
        """
        if status and appindicator:
            self._indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif status and not appindicator:
            self._status_icon.set_from_icon_name(config.attention_icon)
        elif not status and appindicator:
            self._indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        else:
            self._status_icon.set_from_icon_name(config.active_icon)

    def _exit(self, widget):
        """Close Feedindicator.

        Args:
            widget: Gtk widget
        """
        Notify.uninit()
        Gtk.main_quit()

    def _notify(self, title, msg, img=feedindicator.__app_name__):
        """Send feed updates to notify-osd.

        Args:
            title: notification title
            msg: message
            img: image (default: app icon)
        """
        n = Notify.Notification.new(title, msg, img)
        n.show()

    def _open_website(self, widget, url, post_id=None):
        """Open website.

        Args:
            widget: Gtk widget
            url: url to open
            post_id: optional post id to change status to read
        """
        webbrowser.open(url)

        if post_id:
            with SQLite() as db:
                db.s('UPDATE posts SET read="true" WHERE id=?', (post_id,))
            sleep(0.5)
            self._render_menu()

    def _update(self, widget=None, timeroverride=False, starttimer=False):
        """Start updating feeds.

        Args:
            widget: Gtk widget
            timeroverride: if true timer will be overridden
            starttimer: if true timer will be started
        """
        if self._config_manager.stoptimer and not timeroverride:
            return False

        with SQLite() as db:
            if db.s('SELECT COUNT(*) FROM feeds')[0][0] > 0:
                if starttimer:
                    GLib.timeout_add_seconds(self._config_manager.refreshtime,
                                             self._update, True)

                self._loading_menu()
                if db.s('SELECT COUNT(*) FROM feeds')[0][0] != 0:
                    self._feeds_thread = FeedThread(self._finished_update)
                    self._feeds_thread.start()
                    if self._config_manager.show_notifications:
                        if self._config_manager.show_update_notifications:
                            self._notify(feedindicator.__app_name__,
                                         _('Begin updating Feeds.'))
            else:
                self._render_menu()
        return True

    def _finished_update(self, *args):
        """Renders menu and shows notification after updating is finished."""
        if self._feeds_thread is not None and self._feeds_thread.is_alive():
            return

        if self._feeds_thread:
            self._feeds_thread.join()
        sleep(1)
        self._feeds_thread = None
        self._render_menu()

        if self._config_manager.show_notifications:
            with SQLite() as db:
                feeds = db.s('SELECT id, title, img FROM feeds WHERE ' +
                             'feed_url IN (SELECT feed_id FROM posts WHERE ' +
                             'read="false" GROUP BY feed_id LIMIT 50) ORDER' +
                             ' BY (SELECT count(feed_id) AS c FROM posts ' +
                             'WHERE read="false" GROUP BY feed_id ORDER BY ' +
                             'c desc), UPPER(title)')
                for feed in feeds:
                    img = os.path.join(config.app_cache_dir,
                                       feed[2]) if feed[2] else None
                    posts = db.s('SELECT title FROM posts WHERE read=' +
                                 '"false" AND feed_id=? LIMIT 3', (feed[0],))
                    if len(posts) > 0:
                        msg = '\n'.join('* %s' % p[0] for p in posts)
                        self._notify(feed[1], msg, img)
                if len(feeds) == 0:
                    if self._config_manager.show_update_notifications:
                        self._notify(feedindicator.__app_name__,
                                     _('Finished updating feeds.'))

    def _clear_menu(self):
        """Removes all entries from menu."""
        for child in self._menu.get_children():
            child.destroy()

    def _loading_menu(self):
        """Populate a loading menu."""
        self._clear_menu()

        item = Gtk.MenuItem(label=_('Loading'))
        item.set_sensitive(False)
        self._menu.append(item)
        self._menu.show_all()
        if appindicator:
            self._indicator.set_menu(self._menu)
        self._set_status(False)

    def _render_menu(self):
        """Populate the menu."""
        self._clear_menu()

        with SQLite() as db:
            feeds = db.s('SELECT id, title, url, feed_url, (SELECT COUNT(*) ' +
                         'FROM posts WHERE posts.feed_id=feeds.id AND ' +
                         'read="false") AS c FROM feeds ORDER BY c DESC, ' +
                         'UPPER(title)')

            if not self._config_manager.feeds_at_top:
                self._conf_menu(len(feeds) > 0)
                self._menu.append(Gtk.SeparatorMenuItem())

            if len(feeds) > 0:
                self._feeds_menu_header()
                for feed in feeds:
                    posts = db.s('SELECT id, title, url FROM posts WHERE ' +
                                 'feed_id=? AND read="false" ORDER BY id ' +
                                 'LIMIT %d' %
                                 self._config_manager.items_per_feed,
                                 (feed[0],))
                    if self._config_manager.show_unread_feeds:
                        self._feed_submenu(feed, posts)
                    else:
                        if feed[4] > 0:
                            self._feed_submenu(feed, posts)
                if db.s('SELECT COUNT(*) FROM posts WHERE ' +
                        'read="false"')[0][0] == 0:
                    menu_notice = Gtk.MenuItem(label=_('No unread posts.'))
                    menu_notice.set_sensitive(False)
                    self._menu.append(menu_notice)
            else:
                item = Gtk.MenuItem(label=_('No feeds defined!'))
                item.set_sensitive(False)
                self._menu.append(item)

            if self._config_manager.feeds_at_top:
                self._menu.append(Gtk.SeparatorMenuItem())
                self._conf_menu(len(feeds) > 0)

            self._menu.show_all()
            if appindicator:
                self._indicator.set_menu(self._menu)
            self._set_status(db.s('SELECT COUNT(*) FROM posts WHERE ' +
                                  'read="false"')[0][0] > 0)

    def _feeds_menu_header(self):
        """Add items to menu with for all feeds."""
        item = Gtk.MenuItem(label=_('Open all unread'))
        item.connect('activate', self._open_unread, '')
        self._menu.append(item)

        item = Gtk.MenuItem(label=_('Mark all as read'))
        item.connect('activate', self._mark_feed_as_read, '')
        self._menu.append(item)

        item = Gtk.MenuItem(label=_('Mark all as unread'))
        item.connect('activate', self._mark_feed_as_unread)
        self._menu.append(item)

        item = Gtk.MenuItem(label=_('Reload all feeds'))
        item.connect('activate', self._update, True, False)
        self._menu.append(item)
        self._menu.append(Gtk.SeparatorMenuItem())

    def _feed_submenu(self, feed, posts):
        """Add a feed submenu to the menu.

        Args:
            feed: tuple feed info (id, title, url, feed_url, number of posts)
            posts: list of posts to append with (id, title, url) for each post
        """
        menu_header = Gtk.MenuItem('%s (%d)'.replace(' (0)', '') % (feed[1],
                                                                    feed[4]))

        submenu = Gtk.Menu()
        item = Gtk.MenuItem(_('Open Website'))
        item.connect('activate', self._open_website, feed[2])
        submenu.append(item)

        item = Gtk.MenuItem(label=_('Open unread'))
        item.connect('activate', self._open_unread, feed[0])
        submenu.append(item)

        if feed[4] > self._config_manager.items_per_feed:
           item = Gtk.MenuItem(label=_('Open displayed posts'))
           item.connect('activate', self._open_displayed, feed[0])
           submenu.append(item)

        item = Gtk.MenuItem(label=_('Mark as read'))
        item.connect('activate', self._mark_feed_as_read, feed[0])
        submenu.append(item)

        if feed[4] > self._config_manager.items_per_feed:
           item = Gtk.MenuItem(label=_('Mark displayed posts as read'))
           item.connect('activate', self._mark_displayed_as_read, feed[0])
           submenu.append(item)

        item = Gtk.MenuItem(label=_('Mark as unread'))
        item.connect('activate', self._mark_feed_as_unread, feed[0])
        submenu.append(item)

        for i, post in enumerate(posts):
            if i == 0:
                submenu.append(Gtk.SeparatorMenuItem())
            item = Gtk.MenuItem(post[1])
            item.connect('activate', self._open_website, post[2], post[0])
            submenu.append(item)

        menu_header.set_submenu(submenu)
        self._menu.append(menu_header)

    def _conf_menu(self, has_feeds):
        """Adds config items to menu.

        Args:
            has_feeds: if feeds are displayed in the menu
        """
        if self._config_manager.feeds_at_top:
            self._menu.append(Gtk.SeparatorMenuItem())

        item = Gtk.MenuItem(label=_('Add feed'))
        item.connect('activate', AddFeedDialog, self._update, None, True,
                     False)
        self._menu.append(item)

        if has_feeds:
            item = Gtk.CheckMenuItem(label=self._timer_text())
            if self._config_manager.stoptimer:
                item.set_active(False)
            else:
                item.set_active(True)
                item.connect('toggled', self._toggle_update)
                self._menu.append(item)

        menu_configure = Gtk.MenuItem(label=_('Preferences'))
        menu_configure.connect('activate', PreferencesDialog,
                               self._config_manager, self._update, None, True,
                               True)
        self._menu.append(menu_configure)
        menu_about = Gtk.MenuItem(label=_('About'))
        menu_about.connect('activate', AboutDialog)
        self._menu.append(menu_about)
        item = Gtk.MenuItem(label=_('Exit'))
        item.connect('activate', self._exit)
        self._menu.append(item)

    def _open_unread(self, widget, feed_id=None):
        """Opens all unread post of the given feed or all unread posts.

        Args:
            widget: Gtk widget
            feed_id: optional feed id, if not given opens all unread
        """
        with SQLite() as db:
            if feed_id:
                posts = db.s('SELECT url FROM posts WHERE feed_id=? AND ' +
                             'read="false"', (feed_id,))
                for post in posts:
                    webbrowser.open(post[0])
                    sleep(0.6)

                db.s('UPDATE posts SET read="true" WHERE feed_id=?',
                     (feed_id,))
            else:
                for feed in db.s('SELECT id FROM feeds'):
                    posts = db.s('SELECT url FROM posts WHERE feed_id=? AND ' +
                                 'read="false"', feed)
                    for post in posts:
                        webbrowser.open(post[0])
                        sleep(0.6)
                    db.s('UPDATE posts SET read="true" WHERE feed_id=?', feed)
        sleep(0.5)
        self._render_menu()

    def _open_displayed(self, widget, feed_id):
        """Opens all unread post of the given feed or all unread posts.

        Args:
            widget: Gtk widget
            feed_id: optional feed id, if not given opens all unread
        """
        with SQLite() as db:
            posts = db.s('SELECT id, url FROM posts WHERE feed_id=? AND ' +
                         'read="false" ORDER BY id DESC LIMIT %d' %
                         self._config_manager.items_per_feed, (feed_id,))
            for post in posts:
                webbrowser.open(post[1])
                db.s('UPDATE posts SET read="true" WHERE id=?', (post[0],))
                sleep(0.6)
        self._render_menu()

    def _mark_feed_as_read(self, widget, feed_id=None):
        """Mark all posts of all feeds or a specific feed as read.

        Args:
            widget: Gtk widget
            feed_id: optinal feed id, if not given all will be updated
        """
        with SQLite() as db:
            f = 'WHERE feed_id=?' if feed_id else ''
            db.s('UPDATE posts SET read="true" %s' % f,
                 (feed_id,) if feed_id else ())
        sleep(0.5)
        self._render_menu()

    def _mark_displayed_as_read(self, widget, feed_id):
        """Marks displayed posts of given feed as read.

        Args:
            widget: Gtk widget
            feed_id: feed id
        """
        with SQLite() as db:
            db.s('UPDATE posts SET read="true" WHERE feed_id=? AND id IN ' +
                 '(SELECT id FROM posts WHERE feed_id=? AND read="false" ' +
                 'ORDER BY id DESC LIMIT %d)' %
                 self._config_manager.items_per_feed, (feed_id, feed_id))
        sleep(0.5)
        self._render_menu()

    def _mark_feed_as_unread(self, widget, feed_id=None):
        """Mark all posts of all feeds or a specific feed as read.

        Args:
            widget: Gtk widget
            feed_id: optinal feed id, if not given all will be updated
        """
        with SQLite() as db:
            f = 'WHERE feed_id=?' if feed_id else ''
            db.d('UPDATE posts SET read="false" %s' % f,
                 (feed_id,) if feed_id else ())
        sleep(0.5)
        self._render_menu()

    def _toggle_update(self, widget):
        """Toggle timer updating.

        Args:
            widget: Gtk widget
        """
        if self._config_manager.stoptimer:
            self._config_manager.stoptimer = False
            if self._config_manager.show_notifications:
                self._notify(feedindicator.__app_name__, self._timer_text())
            self._update(None, True, True)
        else:
            self._config_manager.stoptimer = True
            if self._config_manager.show_notifications:
                self._notify(config.app_name,
                             _('Feeds will not update automatically.'))

    def _timer_text(self):
        """"Text for timer element."""
        minutes = self._config_manager.refreshtime / 60
        return gettext.ngettext('Update feeds every minute',
                                'Update feeds every %(minutes)d minutes',
                                minutes) % {'minutes': minutes}
