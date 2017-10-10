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
gi.require_version('Notify', '0.7')
import os
import sqlite3
import sys

from argparse import ArgumentParser, RawTextHelpFormatter
from feedindicator import config, feeds, utils
from feedindicator.indicator import AppIndicator
from gi.repository import Gtk, Notify
from time import sleep


def _add_feed(args):
    try:
        feeds.add(args.url)
    except sqlite3.Error as e:
        print(_('Could not add feed.'), e, file=sys.stderr)


def _update_feeds(args):
    try:
        nb_new_posts = feeds.update()
        print(_('Feeds updated. New posts: %(nr)d') % {'nr': nb_new_posts})
    except Exception as e:
        print(_('Error while updating feeds.'), e, file=sys.stderr)


def main():
    gettext.install(feedindicator.__app_name__, config.app_locale_dir,
                    codeset="utf-8")
    Notify.init(feedindicator.__app_name__)

    if not os.path.exists(config.app_cache_dir):
        os.makedirs(config.app_cache_dir)
    if not os.path.exists(config.app_config_dir):
        os.makedirs(config.app_config_dir)
    if not os.path.exists(config.app_data_dir):
        os.makedirs(config.app_data_dir)

    parser = ArgumentParser(prog=feedindicator.__app_name__,
                            description=feedindicator.__description__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version',
                        version=utils.app_version())
    parser.add_argument('--autostarted', action='store_true', help='Option ' +
                        'to indicate feedindicator was autostarted.')
    subparsers = parser.add_subparsers(dest='subparser')

    # create the parser for the "add" subcommand
    add_parser = subparsers.add_parser('add', help='Add a new feed.')
    add_parser.set_defaults(func=_add_feed)
    add_parser.add_argument('url', help='Feed URL')

    # create the parser for the "update" subcommand
    update_parser = subparsers.add_parser('update', help='Update feeds.')
    update_parser.set_defaults(func=_update_feeds)

    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    if args.autostarted:
        sleep(5)

    config_manager = config.ConfigManager()
    config_manager.load()

    try:
        utils.db_init()
    except sqlite3.Error as e:
        print(_('Could not init database.'), e, file=sys.stderr)

    if args.subparser:
        args.func(args)
    else:
        indicator = AppIndicator(config_manager)
        Gtk.main()
