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
from xdg import BaseDirectory

path = {
        'fmm': '/etc/fmm/fmm.ini',
        'users': '/etc/fmm/users.ini',
        'feedsettings': '/etc/fmm/feedsettings.ini'
}

default_settings = {
        'smtp-from': 'fmm@localhost',
        'smtp-host': 'localhost',
        'smtp-port': 25,
        'smtp-sec': 'NONE',
        'smtp-username': '',
        'smtp-password': '',
        'smtp-keyfile': '',
        'smtp-certfile': ''
}

default_user_config = {
        'feed-list': None,
        'name': None
}

default_feed_config = {
        'template-name': None,
        'template-type': 'html',
        'list-id': 'FMM'
}

def load_feedlist(filename):
    feeds = list()
    with open(os.path.join('/usr/share/fmm/lists', filename)) as f:
        for feed in f.read().split('\n'):
            if len(feed) == 0:
                continue
            feeds.append(feed)
    return feeds;

def settings():
    print('Loading settings')
    cp = configparser.ConfigParser()
    cp.read(path['fmm'])
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
    cp.read(path['users'])
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
    cp.read(path['feedsettings'])
    default_config = default_feed_config

    if 'DEFAULT' in cp:
        for k, v in default_config.items():
            if k in cp['DEFAULT']:
                default_config[k] = cp['DEFAULT'][k]

    feedconf['DEFAULT'] = default_config.copy()

    for section in cp:
        if section == 'DEFAULT':
            continue

        feed = default_config.copy()

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
    return os.path.join('/var/lib/fmm/feeds',
            '{}-{}.json'.format(hashlib.sha1(url.encode('UTF-8')).hexdigest()[:10],
            slugify(url)))

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

    feedspath = '/var/lib/fmm/feeds/'

    if not os.path.exists(feedspath):
        os.mkdir(feedspath)

    for url, data in feeds.items():
        filename = feedfile(url)
        with open(filename, 'w') as f:
            json.dump(data['state'], f)
