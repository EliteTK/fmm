# Config related functionality

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

def read_feeds(filename):
    feeds = list()
    with open(filename) as f:
        for feed in f.read().split('\n'):
            if len(feed) == 0:
                continue
            feeds.append(feed)
    return feeds;

def load_settings():
    print('Loading settings')
    global settings
    cp = configparser.ConfigParser()
    cp.read('fmm.ini')
    default_config = default_settings

    if 'DEFAULT' in cp:
        for k, v in default_config.items():
            if k in cp['DEFAULT']:
                default_config[k] = cp['DEFAULT'][k]

    settings = default_config

def load_users():
    print('Loading users')
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
        user = default_config

        for k, v in user.items():
            if k in cp[section]:
                user[k] = cp[section][k]

        user['subscriptions'] = read_feeds(user['feed-list'])

        users[section] = user

    return users

def load_feed_settings():
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
