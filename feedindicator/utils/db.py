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

from feedindicator import config
from feedindicator.utils.sqlite import SQLite


def init():
    """Init SQLite database, creates tables."""
    if not os.path.exists(config.app_database):
        print(_('No database found, creating it.'))

        with SQLite() as db:
            db.s('CREATE TABLE feeds (id integer NOT NULL PRIMARY KEY ' +
                 'AUTOINCREMENT, created_at datetime NOT NULL DEFAULT ' +
                 'CURRENT_TIMESTAMP, updated_at datetime NOT NULL DEFAULT ' +
                 'CURRENT_TIMESTAMP, feed_url TEXT NOT NULL UNIQUE, url ' +
                 'TEXT, title TEXT, img TEXT)')
            db.s('CREATE TRIGGER feeds_updated_at_trigger AFTER UPDATE ON ' +
                 'feeds FOR EACH ROW BEGIN UPDATE feeds SET ' +
                 'updated_at=CURRENT_TIMESTAMP WHERE id=old.id; END')
            db.s('CREATE TABLE posts (id integer NOT NULL PRIMARY KEY ' +
                 'AUTOINCREMENT, created_at datetime NOT NULL DEFAULT ' +
                 'CURRENT_TIMESTAMP, updated_at datetime NOT NULL DEFAULT ' +
                 'CURRENT_TIMESTAMP, hash TEXT NOT NULL UNIQUE, url TEXT, ' +
                 'title TEXT, raw TEXT, read BOOLEAN DEFAULT false, feed_id ' +
                 'integer NOT NULL, FOREIGN KEY(feed_id) REFERENCES ' +
                 'feeds(id))')
            db.s('CREATE INDEX posts_feed_id_idx ON posts(feed_id)')
            db.s('CREATE TRIGGER posts_updated_at_trigger AFTER UPDATE ON ' +
                 'posts FOR EACH ROW BEGIN UPDATE posts SET ' +
                 'updated_at=CURRENT_TIMESTAMP WHERE id=old.id; END')
        print(_('Database created.'))
