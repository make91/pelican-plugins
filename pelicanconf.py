#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Ondřej Grover'
SITENAME = 'Pelican i18n_subsites plugin'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Prague'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         )

# Social widget
SOCIAL = (
        ('github', 'https://github.com/smartass101/'),
          )

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PLUGIN_PATH = "/home/ondrej/projects/pelican/repos/pelican-plugins"
PLUGINS = ["i18n_subsites"]

JINJA_EXTENSIONS = ['jinja2.ext.i18n']

THEME = 'themes/notmyidea/'

DEFAULT_LANG = "en"
I18N_SUBSITES = {
        'cz': {
            'SITENAME': 'Pelican i18n_subsites doplňek',
            },
        }
