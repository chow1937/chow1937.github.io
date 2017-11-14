#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'tonychow'
SITENAME = u"Tonychow's Blog"
SITEURL = 'http://blog.tonychow.me'
SITELOGO = '/images/avatar.jpg'
SITESUBTITLE = 'Go/Python backend developer'
SITEDESCRIPTION = '%s\'s Thoughts and Writings' % AUTHOR
ROBOTS = 'index, follow'

BROWSER_COLOR = '#333333'

PATH = 'content/articles'
STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/custom.css': {'path': 'static/custom.css'},
}
THEME = 'themes/Flex'

MAIN_MENU = True
SUMMARY_MAX_LENGTH = None

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = ()

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# Flex configs
PYGMENTS_STYLE = 'colorful'
COPYRIGHT_YEAR = 2017
CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

MENUITEMS = (
    ('Archives', '/archives.html'),
    ('Categories', '/categories.html'),
    ('Tags', '/tags.html'),
)

PLUGIN_PATHS = ['plugins']
PLUGINS = [
    'sitemap',
    'post_stats',
    'i18n_subsites',
    'summary',
]

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.6,
        'indexes': 0.6,
        'pages': 0.5,
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly',
    }
}

SOCIAL = (
    ('github', 'https://github.com/chow1937'),
)
