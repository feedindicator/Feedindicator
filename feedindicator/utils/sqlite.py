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


import sqlite3

from feedindicator import config


class SQLite:
    """SQlite database wrapper.

    Attributes:
        _con: database connection
    """
    def __init__(self):
        self._con = None

    def get_con(self):
        """Get database connection."""
        return self._con

    con = property(get_con)

    def __enter__(self):
        self.open(config.app_database)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self, path):
        """Opens a new connection.

        Args:
            path: path to sqlite database file
        """
        self._con = sqlite3.connect(path)

    def close(self):
        """Closes the current connection."""
        if self._con:
            self._con.close()

    def s(self, query, data=(), auto_commit=True):
        """Executes the given query and returns the results.

        Args:
            query: SQL query
            data: optinal additional data
            auto_commit: if true commits after query execution
        """
        if not self._con:
            self.open(config.app_database)
        cur = self._con.cursor()
        if data == ():
            cur.execute(query)
        else:
            cur.execute(query, data)
        rows = cur.fetchall()
        if auto_commit:
            self.commit()
        return rows

    def many(self, query, data, auto_commit=True):
        """Executes the given query with executemany() function.

        Args:
            query: SQL query
            data: additional data
            auto_commit: if true commits after query execution
        """
        if not self._con:
            self.open(config.app_database)
        cur = self._con.cursor()
        cur.executemany(query, data)
        if auto_commit:
            self.commit()

    def commit(self):
        """Commit changes to the database. When an error occurs a roll back
            is done.
        """
        if not self._con:
            self.open(config.app_database)
        try:
            self._con.commit()
        except sqlite3.Error as e:
            self._con.rollback()
            raise e
