#! /usr/bin/env python3
from setuptools import setup, find_packages

setup(name='fmm',
      version='0.1',
      description='An Atom and RSS feed to E-Mail "converter"',
      long_description=open('README.md').read(),
      author='Tomasz Kramkowski',
      author_email='tk@the-tk.com',
      url='http://github.com/EliteTK/fmm',
      packages=['fmm'],
      scripts=['bin/fmm'],
      package_data={'fmm': ['README.md']},
      data_files=[('share/doc/fmm', ['README.md', 'LICENSE']),
                  ('/etc/fmm', ['data/fmm.ini',
                                'data/users.ini',
                                'data/feedsettings.ini']),
                  ('/usr/share/fmm/lists', ['data/default.feeds']),
                  ('/usr/share/fmm/templates', ['data/default.html']),
                  ('/usr/lib/systemd/system', ['systemd/fmm.service',
                                               'systemd/fmm.timer'])
                  ],
      requires=['slugify', 'xdg', 'feedparser', 'jinja2'],
      license='GPLv3')
