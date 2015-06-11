# Feed setup functionality

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

import configparser
import hashlib
from slugify import slugify
import os
import json

default_settings = {
        'smtp-from': 'fmm@fmm.com',
        'smtp-server': None,
        'smtp-options': ''
}

default_user_config = {
        'feed-list': None,
        'name': None
}

default_feed_config = {
        'template-name': None,
        'template-type': None,
        'list-id': 'Feed Me Mail'
}

def load_feedlist(filename):
    feeds = list()
    with open(filename) as f:
        for feed in f.read().split('\n'):
            if len(feed) == 0:
                continue
            feeds.append(feed)
    return feeds;

def config():
    print('Loading settings')
    cp = configparser.ConfigParser()
    cp.read('fmm.ini')
    default_config = default_settings

    if 'DEFAULT' in cp:
        for k, v in default_config.items():
            if k in cp['DEFAULT']:
                default_config[k] = cp['DEFAULT'][k]

    return default_config

def users():
    print('Creating list of users')
    users = dict()

    cp = configparser.ConfigParser()
    cp.read('users.ini')
    default_config = default_user_config

    if 'DEFAULT' in cp:
        for k, v in default_config.items():
            if k in cp['DEFAULT']:
                default_config[k] = cp['DEFAULT'][k]

    for section in cp:
        if section == 'DEFAULT':
            continue

        user = dict()
        user['config'] = default_config

        for k, v in user.items():
            if k in cp[section]:
                user['config'][k] = cp[section][k]

        user['subscriptions'] = load_feedlist(user['config']['feed-list'])

        users[section] = user

    return users

def feed_settings():
    print('Loading feed settings')
    feedconf = dict()

    cp = configparser.ConfigParser()
    cp.read('feedsettings.ini')
    default_config = default_feed_config

    if 'DEFAULT' in cp:
        for k, v in default_config.items():
            if k in cp['DEFAULT']:
                default_config[k] = cp['DEFAULT'][k]

    feedconf['DEFAULT'] = default_config

    for section in cp:
        if section == 'DEFAULT':
            continue
        feed = default_config

        for k, v in feed.items():
            if k in cp[section]:
                feed[k] = cp[section][k]

        feedconf[section] = feed

    return feedconf

def subscriptions(users):
    print('Creating list of subscriptions')
    subscriptions = list()

    for email, info in users.items():
        subscriptions.extend(info['subscriptions'])

    return list(set(subscriptions))

def feedfile(url):
    return 'feeds/{}-{}.json'.format(hashlib.sha1(url.encode('UTF-8')).hexdigest()[:10],
            slugify(url))

def get_feed_state(url):
    ffile = feedfile(url)

    if os.path.exists(ffile):
        with open(ffile) as f:
            return json.load(f)
    else:
        return {'type': 'Unknown'}

def feeds(users, subscriptions, feedconf):
    print('Creating list of feeds')
    feeds = dict()

    for sub in subscriptions:
        feeds[sub] = dict()
        if sub in feedconf:
            feeds[sub]['config'] = feedconf[sub]
        else:
            feeds[sub]['config'] = feedconf['DEFAULT']

        feeds[sub]['subscribers'] = dict()

        for email, data in users.items():
            if sub in data['subscriptions']:
                feeds[sub]['subscribers'][email] = data['config']

        feeds[sub]['state'] = get_feed_state(sub)

        feeds[sub]['url'] = sub

    return feeds

def save_feed_states(feeds):
    print('Saving feed states')

    if not os.path.exists('feeds'):
        os.mkdir('feeds')

    for url, data in feeds.items():
        filename = feedfile(url)
        with open(filename, 'w') as f:
            json.dump(data['state'], f)
