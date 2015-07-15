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

import os, time, smtplib
from email.mime.text import MIMEText
from jinja2 import FileSystemLoader, Environment

feed_attrs = [
        'author',
        'author_detail',
        'cloud',
        'contributors',
        'docs',
        'errorreportsto',
        'generator',
        'generator_detail',
        'icon',
        'id',
        'image',
        'info',
        'info_detail',
        'language',
        'license',
        'link',
        'links',
        'logo',
        'published',
        'published_parsed',
        'publisher',
        'publisher_detail',
        'rights',
        'rights_detail',
        'subtitle',
        'subtitle_detail',
        'tags',
        'textinput',
        'title',
        'title_detail',
        'ttl',
        'updated',
        'updated_parsed'
]

entry_attrs = [
        'author',
        'author_detail',
        'comments',
        'content',
        'contributors',
        'created',
        'created_parsed',
        'enclosures',
        'expired',
        'expired_parsed',
        'id',
        'license',
        'link',
        'links',
        'published',
        'published_parsed',
        'publisher',
        'publisher_detail',
        'source',
        'summary',
        'summary_detail',
        'tags',
        'title',
        'title_detail',
        'updated',
        'updated_parsed'
]

tfuncs = {
        'strftime': time.strftime
}

def gen_channel_tenv(channel):
    tenv = dict()
    for attr in feed_attrs:
        tenv[attr] = channel.get(attr, None)
    return tenv

def gen_item_tenv(item):
    tenv = dict()
    for attr in entry_attrs:
        tenv[attr] = item.get(attr, None)
    return tenv

def get_tenv(channel, item):
    return {'channel': channel, 'item': item, 'func': tfuncs}

def render_content(channel_tenv, item_tenv, template):
    template = os.path.join('/usr/share/fmm/templates', template)
    template_name = os.path.basename(template)
    template_dir = os.path.dirname(template)
    l = FileSystemLoader(template_dir)
    e = Environment(loader=l)
    t = e.get_template(template_name)
    return t.render(get_tenv(channel_tenv, item_tenv))

def sendemails(emails):
    print('Connecting to {}:{}'.format(settings['smtp-host'], settings['smtp-port']))
    if settings['smtp-sec'] == 'NONE' or settings['smtp-sec'] == '':
        s = smtplib.SMTP(settings['smtp-host'], settings['smtp-port'])
    elif settings['smtp-sec'] == 'STARTTLS':
        s = smtplib.SMTP(settings['smtp-host'], settings['smtp-port'])
        s.starttls(settings['smtp-keyfile'], settings['smtp-certfile'])
        s.ehlo() #Needed?
    elif settings['smtp-sec'] == 'SSL/TLS':
        s = smtplib.SMTP_SSL(settings['smtp-host'], settings['smtp-port'],
                             keyfile=settings['smtp-keyfile'],
                             certfile=settings['smtp-certfile'])
    else:
        print("Invalid smtp-sec setting: `{}'")
        print("Allowed values are `NONE', `STARTTLS', `SSL/TLS'.")
        print("(Default: `NONE')")
        exit(1)

    if len(settings['smtp-username']) > 0:
        s.login(settings['smtp-username'], settings['smtp-password'])

    print('Sending emails')
    for n, email in enumerate(emails):
        print("Sending {}/{}: `{}' to {}".format(n + 1, len(emails),
                                                  email['Subject'],
                                                  email['To']))
        s.send_message(email)

    s.quit()

def send(feeds, _settings):
    global settings
    settings = _settings
    emails = list()

    for url, data in feeds.items():
        if data['data'] is None or len(data['data']['items']) == 0:
            continue

        for item in data['data']['items']:
            content = render_content(gen_channel_tenv(data['data']['channel']),
                    gen_item_tenv(item), data['config']['template-name'])

            subject = data['data']['channel']['title']

            if len(item['title']) > 0:
                subject = '{} - {}'.format(subject, item['title'])

            subject = ' '.join(subject.splitlines())

            for email, info in data['subscribers'].items():
                message = MIMEText(content, data['config']['template-type'])

                message['Subject'] = subject

                message['List-Id'] = data['config']['list-id']
                message['From'] = settings['smtp-from']

                message['To'] = email
                emails.append(message)

    if len(emails):
        sendemails(emails)
