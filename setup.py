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
      data_files=[('share/doc/fmm', ['README.md', 'LICENSE'])],
      license='GPLv3')
