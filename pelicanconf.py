#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'smartass101'
SITENAME = "smartass101's Pelican plugins"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Prague'


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

LOCALE = 'en_US'

I18N_SUBSITES = {
        'cz': {
            'SITENAME': 'smartass101ovy Pelican doplňky',
            'LOCALE': 'cs_CZ',            #This is somewhat redundant with DATE_FORMATS, but IMHO more convenient
            },
        }


DEFAULT_CATEGORY = 'misc'

OUTPUT_SOURCES = True

languages_lookup = {
    'en': 'English',
    'cz': 'Čeština',
    }

def lookup_lang_name(lang_code):
   return languages_lookup[lang_code]

JINJA_FILTERS = {
    'lookup_lang_name': lookup_lang_name,
    }

STATIC_PATHS = ['images', 'files']

EXTRA_PATH_METADATA = {
    'files/.nojekyll': {
        'path': '.nojekyll',
        },
    }
