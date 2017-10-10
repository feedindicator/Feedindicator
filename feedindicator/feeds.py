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


import feedparser
import json
import os
import urllib.request
import sys

from feedindicator import config, utils
from feedindicator.utils import SQLite


# clear out the html element list so all are removed
feedparser._HTMLSanitizer.acceptable_elements = []


def add(url):
    """Add a new feed url to the database.

    Args:
        url: feed url
    """
    with SQLite() as db:
        db.s('INSERT INTO feeds (feed_url) VALUES (?)', (url,))
        print(_('Feed added.'))


def delete(feed_id):
    """Delete a feed and all its posts from the database.

    Args:
        feed_id: feed id
    """
    with SQLite() as db:
        img = db.s('SELECT img FROM feeds WHERE id=?', (feed_id,))[0][0]
        if img and os.path.exists(os.path.join(config.app_cache_dir, img)):
            os.remove(os.path.join(config.app_cache_dir, img))
        db.s('DELETE FROM posts WHERE feed_id=?', (feed_id,))
        db.s('DELETE FROM feeds WHERE id=?', (feed_id,))


def update():
    """Update all feeds."""
    new_posts = 0
    with SQLite() as db:
        feeds = db.s('SELECT id, feed_url, title, url, img FROM feeds')
        for feed in feeds:
            result = _parse_feed(feed[1])
            if not result['success']:
                continue

            if feed[2] == None:
                db.s('UPDATE feeds SET title=? WHERE id=?',
                     (result['feed']['title'], feed[0]))
            if feed[3] != result['feed']['link']:
                db.s('UPDATE feeds SET url=? WHERE id=?',
                     (result['feed']['link'], feed[0]))
            if not result['feed']['img']:
                db.s('UPDATE feeds SET img=? WHERE id=?',
                     (result['feed']['img'], feed[0]))

            items = ()
            hashes = ()
            for p in result['posts']:
                hash = utils.get_hash(p['date'], p['title'])
                hashes += (hash,)
                if db.s('SELECT COUNT(*) FROM posts WHERE hash=?',
                        (hash,))[0][0] == 0:
                    items += ((hash, p['link'], p['title'],
                               json.dumps(p['raw']), feed[0]),)

            new_posts += len(items)
            if len(items) > 0:
                db.many('INSERT INTO posts (hash, url, title, raw, feed_id) ' +
                        'VALUES (?,?,?,?,?)', items)
            db.s('DELETE FROM posts WHERE read="true" AND hash NOT IN '
                 '(%s) AND feed_id=?' % ','.join('?' for p in hashes),
                 hashes + (feed[0],))
    return new_posts


def _parse_feed(url):
    """Parses a feed and returns the data.

    Args:
        url: feed url
    """
    result = {
        'feed': {},
        'posts': [],
        'success': False
    }

    try:
        rssfeed = feedparser.parse(url)
        posts = []
        for e in rssfeed.entries:
            e.title = e.title.replace('\n', '')
            if len(e.title) > 72:
                substr = e.title[:72].rpartition(' ')
                if substr[0] != '':
                    e.title = substr[0] + '...'

            date = None
            if 'published' in e:
                date = e.published
            elif 'updated' in e:
                date = e.updated
            elif 'created' in e:
                date = e.created
            posts.append({
                'title': e.title,
                'link': e.link,
                'date': date,
                'raw': e
            })
        result['posts'] = posts
        feedimg = None
        webimg = None
        if 'image' in rssfeed.feed:
            if 'href' in rssfeed.feed.image:
                webimg = rssfeed.feed.image.href
            elif 'url' in rssfeed.feed.image:
                webimg = rssfeed.feed.image.url
            elif 'logo' in rssfeed.feed:
                webimg = rssfeed.feed.logo
            elif 'icon' in rssfeed.feed:
                webimg = rssfeed.feed.icon
        if webimg != None:
            ext = webimg.rsplit('.', 1)
            if len(ext[1]) > 5 or len(ext[1]) == 0:
                ext[0] = webimg
                ext[1] = 'jpg'
            shash = hashlib.sha512(url.encode('utf-8')).hexdigest()
            localimg = os.path.join(config.app_cache_dir,
                                    '%s.%s' % (shash, ext[1]))
            feedimg = '%s.%s' % (shash, ext[1])

            request = urllib.request.Request(webimg)
            with urllib.request.urlopen(request) as response:
                with open(localimg, 'bw') as f:
                    f.write(response.read())

        result['feed'] = {
            'title': rssfeed.feed.title,
            'link': rssfeed.feed.link,
            'img': feedimg
        }
        result['success'] = True
    except Exception as e:
        print('Error while parsing feed (feed url: %s).' % url, e,
              file=sys.stderr)
    return result
