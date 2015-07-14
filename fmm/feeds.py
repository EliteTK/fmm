# Feed related functionality

# Copyright (C) 2015  Tomasz Kramkowski

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import feedparser
import hashlib
import json

def construct_feed(url, channel, items, users, feeds):
    feed_construct = dict()
    feed_construct['url'] = url
    feed_construct['channel'] = tenv.gen_channel_tenv(channel)

    feed_construct['items'] = list()
    for item in items:
        feed_construct['items'].append(tenv.gen_item_tenv(item))

    feed_construct['subscribers'] = dict()
    for email, info in users.items():
        if url in info['subscriptions']:
            feed_construct['subscribers'][email] = info

    feed_construct['config'] = feeds[url]

    return feed_construct

def json_load_empty(f):
    try:
        return json.load(f)
    except ValueError:
        return dict()

def handle_feed_status(feedfile, status):
    pass

def feed_update_method(feedfile):
    if not os.path.exists(feedfile):
        return None
    with open(feedfile) as f:
        feeddata = json_load_empty(f)
        try:
            return feeddata['type']
        except KeyError:
            return None

def itemhash(item):
    return hashlib.sha1(item['id'].encode('UTF-8')).hexdigest()

def hashlist(items):
    hashes = list()
    for item in items:
        hashes.append(itemhash(item))
    return hashes

def init_feed(feed):
    print('Initialising feed at {}'.format(feed['url']))
    parsed = feedparser.parse(feed['url'])

    if parsed.status != 200:
        print('Error {}'.format(parsed.status))
        return

    hashes = hashlist(parsed['items'])

    try:
        etag = parsed.etag
    except AttributeError:
        etag = None

    try:
        modified = parsed.modified
    except AttributeError:
        modified = None

    if etag:
        feed['state']['type'] = 'ETags'
        feed['state']['etag'] = parsed.etag
        feed['state']['sums'] = hashes
    elif modified:
        feed['state']['type'] = 'Last-Modified'
        feed['state']['lm'] = parsed.modified
        feed['state']['sums'] = hashes
    else:
        feed['state']['type'] = 'Basic'
        feed['state']['sums'] = hashes

    print('Feed is of type {}'.format(feed['state']['type']))
    print('Found {} items'.format(len(parsed['items'])))

    feed['data'] = {'channel': parsed['channel'], 'items': parsed['items']}

def remove_old_items(feed):
    feed['data']['items'] = list(filter(lambda item: itemhash(item) not in feed['state']['sums'], feed['data']['items']))

def etags_feed(feed):
    print('Polling ETags feed at {}'.format(feed['url']))
    feed['state']['type'] = 'ETags'

    try:
        feedetag = feed['state']['etag']
    except KeyError:
        feedetag = None


    parsed = feedparser.parse(feed['url'], etag=feedetag)

    if parsed.status == 304:
        print('No new items')
        feed['data'] = None
        return
    elif parsed.status != 200:
        print('Error {}'.format(parsed.status))
        return

    if feedetag != parsed.etag:
        print('ETags differ, expecting new feeds')

    feed['state']['etag'] = parsed.etag

    feed['data'] = {'channel': parsed['channel'], 'items': parsed['items']}
    remove_old_items(feed)
    print('Found {} new items'.format(len(feed['data']['items'])))

    feed['state']['sums'].extend(hashlist(feed['data']['items']))

def lm_feed(feed):
    print('Polling Last-Modified feed at {}'.format(feed['url']))
    feed['state']['type'] = 'Last-Modified'

    try:
        last_modified = feed['state']['lm']
    except KeyError:
        last_modified = None

    parsed = feedparser.parse(feed['url'], modified=last_modified)

    if parsed.status == 304:
        print('No new items')
        feed['data'] = None
        return
    elif parsed.status != 200:
        print('Status {} returned.')
        return

    if last_modified != parsed.modified:
        print('Last-Modified dates differ, expecting new feeds')

    feed['state']['lm'] = parsed.modified

    feed['data'] = {'channel': parsed['channel'], 'items': parsed['items']}
    remove_old_items(feed)
    print('Found {} new items'.format(len(feed['data']['items'])))

    feed['state']['sums'].extend(hashlist(feed['data']['items']))

def basic_feed(feed):
    print('Polling Basic feed at {}'.format(feed['url']))
    feed['state']['type'] = 'Basic'

    parsed = feedparser.parse(feed['url'])

    feed['data'] = {'channel': parsed['channel'], 'items': parsed['items']}
    remove_old_items(feed)
    print('Found {} new items'.format(len(feed['data']['items'])))

    feed['state']['sums'].extend(hashlist(feed['data']['items']))

def grab(feeds):
    print('Grabbing feeds')
    for url, data in feeds.items():
        if data['state']['type'] == "ETags":
            etags_feed(feeds[url])
        elif data['state']['type'] == "Last-Modified":
            lm_feed(feeds[url])
        elif data['state']['type'] == "Basic":
            basic_feed(feeds[url])
        else:
            init_feed(feeds[url])
