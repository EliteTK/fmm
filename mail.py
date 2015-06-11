# Mail sending and templating functionality

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

import os
from email.mime.text import MIMEText
from jinja2 import FileSystemLoader, Environment

channel_atts = [
        'title',
        'link',
        'description',
        'language',
        'copyright',
        'managingEditor',
        'webMaster',
        'pubDate',
        'lastBuildDate',
        'category',
        'generator',
        'docs',
        'cloud',
        'ttl',
        'image',
        'image',
        'rating',
        'textInput',
        'skipHours',
        'skipDays'
        ]

item_attrs = [
        'title',
        'link',
        'description',
        'author',
        'category',
        'comments',
        'enclosure',
        'guid',
        'pubDate',
        'source'
        ]

def gen_channel_tenv(channel):
    tenv = dict()
    for attr in channel_atts:
        tenv[attr] = channel.get(attr, None)
    return tenv

def gen_item_tenv(item):
    tenv = dict()
    for attr in item_attrs:
        tenv[attr] = item.get(attr, None)
    return tenv

def get_tenv(channel, item):
    return {'channel': channel, 'item': item}

def render_content(channel_tenv, item_tenv, template):
    template_name = os.path.basename(template)
    template_dir = os.path.dirname(template)
    l = FileSystemLoader(template_dir)
    e = Environment(loader=l)
    t = e.get_template(template_name)
    return t.render(get_tenv(channel_tenv, item_tenv))

def send_item(channel, item):
    pass

def sendmail(content):
    command = '{} {}'.format(settings['smtp-server'], settings['smtp-options'])
    p = os.popen(command, 'w')
    p.write(content)
    p.close()

def send(feeds, _settings):
    print('Sending emails')
    global settings
    settings = _settings
    emails = list()

    for url, data in feeds.items():
        if data['data'] is None or len(data['data']['items']) == 0:
            continue

        for item in data['data']['items']:
            content = render_content(data['data']['channel'], item, data['config']['template-name'])

            subject = data['data']['channel']['title']

            if len(item['title']) > 0:
                subject = '{} - {}'.format(subject, item['title'])

            for email, info in data['subscribers'].items():
                message = MIMEText(content, data['config']['template-type'])

                message['Subject'] = subject

                message['List-Id'] = data['config']['list-id']
                message['From'] = settings['smtp-from']

                message['To'] = email
                emails.append(message.as_string())

    for email in emails:
        sendmail(email)