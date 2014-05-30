"""i18n_subsites plugin creates i18n-ized subsites of the default site

This plugin is designed for Pelican 3.4 and later
"""


import os
import six
import logging
import posixpath

from itertools import chain
from collections import OrderedDict
from contextlib import contextmanager
from six.moves.urllib.parse import urlparse, urljoin

import gettext
import locale

from pelican import signals
from pelican.generators import ArticlesGenerator, PagesGenerator
from pelican.settings import configure_settings


# Global vars
# map: generator_type -> [contents, other_contents, other_status, translations,
# other_translations]
_GENERATOR_ATTRS = {
    ArticlesGenerator :
    ['articles', 'drafts', 'draft', 'translations', 'drafts_translations'],
    PagesGenerator :
    ['pages', 'hidden_pages', 'hidden', 'translations', 'hidden_translations'],
    }
_LOGGER = logging.getLogger(__name__)


@contextmanager
def temporary_locale(temp_locale=None):
    '''Enable code to run in a context with a temporary locale

    Resets the locale back when exiting context.
    Can set a temporary locale if provided
    '''
    orig_locale = locale.setlocale(locale.LC_ALL)
    if temp_locale is not None:
        locale.setlocale(locale.LC_ALL, temp_locale)
    yield
    locale.setlocale(locale.LC_ALL, orig_locale)


def _get_known_attrs_names(generator):
    '''Get relevant attribute names known for the generator class'''
    clss = set(generator.__class__.__mro__).intersection(
        _GENERATOR_ATTRS.keys())
    if len(clss) != 0:
        cls = clss.pop()
    else:
        raise TypeError('Uknown class {}, cannot access attributes'.format(
            generator))
    if len(clss) > 1:
        _LOGGER.warning(('Ambiguous class mro {} for {}, using class {} '
                        'information to access attributes').format(
                            generator.__mro__, generator, cls))
    return _GENERATOR_ATTRS[cls]


def _get_contents_attrs(generator):
    '''Get the relevant contents attributes from the generator'''
    attrs = _get_known_attrs_names(generator)
    return getattr(generator, attrs[0]), getattr(generator, attrs[1]), attrs[2]


def _set_translations_attrs(generator, translations, other_translations):
    '''Set the relevant translations attributes of the generator'''
    attrs = _get_known_attrs_names(generator)
    setattr(generator, attrs[3], translations)
    setattr(generator, attrs[4], other_translations)

# map: signal name -> SubsitesCreator method name
_SIGNALS_HANDLERS_DB = {'initialized': 'initialized_handler',
    'article_generator_pretaxonomy': 'filter_generator_contents',
    'page_generator_finalized': 'filter_generator_contents',
    'get_writer': 'create_next_subsite',
    'static_generator_finalized': 'save_main_static_files',
}

class SubsitesCreator(object):
    '''Class that controls the generation of subsites'''

    # settings dict of the main site
    main_settings = None

    # map: lang -> subsite siteurl
    subsite_db = {}

    # TODO no difference between subsites? just use site_db including main site?
    

    def __init__(self):
        '''Initialize internal DBs and register signal handlers'''
        self.main_settings = None

    def register(self):
        '''Register the plugin only if required signals are available'''
        for sig_name in _SIGNALS_HANDLERS_DB.keys():
            if not hasattr(signals, sig_name):
                _LOGGER.error('The i18n_subsites plugin requires the {} '
                     'signal available for sure in Pelican 3.4.0 and later, '
                     'plugin will not be used.'.format(sig_name))
                return

        for sig_name, handler_name in _SIGNALS_HANDLERS_DB:
            sig = getattr(signals, sig_name)
            handler = getattr(self, handler_name)
            sig.connect(handler)

    def initialize_dbs(self, settings):
        '''Initialize internal DBs using the Pelican settings dict

        This clears the DBs for e.g. autoreload mode to work
        '''
        self.main_settings = settings
        self.main_siteurl = settings['SITEURL']
        self.subsite_queue = settings.get('I18N_SUBSITES', {}).copy()
        # clear databases in case of autoreload mode
        self.subsite_db = {}
        self.subsite_relurl_db = {}
        self.content_db = {}
        self.generators = []

    @staticmethod
    def disable_lang_variables(settings):
        '''Disable lang specific url and save_as variables for articles, pages

        e.g. ARTICLE_LANG_URL = ARTICLE_URL
        They would conflict with this plugin otherwise.
        '''
        for content in ['ARTICLE', 'PAGE']:
            for meta in ['_URL', '_SAVE_AS']:
                settings[content + '_LANG' + meta] = settings[content + meta]


    def initialized_handler(self, pelican_obj):
        """Initialize plugin variables and Pelican settings
        """
        settings = pelican_obj.settings
        self.disable_lang_variables(settings)
        if self.main_settings is None:
            self.initialize_dbs(settings)

    def relative_to_siteurl(self, url, siteurl=None):
        '''Make an absoulte url relative to the given siteurl

        the siteurl of the main site is used if not given
        '''
        if siteurl is None:
            siteurl = self.main_siteurl
        parsed = urlparse(url)
        path = posixpath.relpath(parsed.path, urlparse(siteurl).path)
        return path


    def filter_generator_contents(self, generator):
        """Filter the contents lists of a generator

        Empty the (other_)translations attribute of the generator to
        prevent generating the translations as they will be generated in
        lang sub-sites.

        Hide content without a translation for current DEFAULT_LANG if
        HIDE_UNTRANSLATED_CONTENT is True
        """
        _set_translations_attrs(generator, [], [])
        self.generators.append(generator)

        hide_untrans = generator.settings.get('HIDE_UNTRANSLATED_CONTENT', True)
        contents, other_contents, status = _get_contents_attrs(generator)
        current_lang = generator.settings['DEFAULT_LANG']
        for content in contents[:]:   # loop over copy for removing
            if content.lang == current_lang:
                self.content_db[content.source_path] = content
            elif hide_untrans:
                content.status = status
                contents.remove(content)
                other_contents.append(content)

    def install_templates_translations(self, generator):
        '''Install gettext translations in the jinja2.Environment

        Only if the 'jinja2.ext.i18n' jinja2 extension is enabled
        the translations for the current DEFAULT_LANG are installed.
        '''
        if 'jinja2.ext.i18n' in generator.settings['JINJA_EXTENSIONS']:
            domain = generator.settings.get('I18N_GETTEXT_DOMAIN', 'messages')
            localedir = generator.settings.get('I18N_GETTEXT_LOCALEDIR')
            if localedir is None:
                localedir = os.path.join(generator.theme, 'translations')
            current_lang = generator.settings['DEFAULT_LANG']
            if current_lang == generator.settings.get('I18N_TEMPLATES_LANG',
                                            self.main_settings['DEFAULT_LANG']):
                translations = gettext.NullTranslations()
            else:
                langs = [current_lang]
                try:
                    translations = gettext.translation(domain, localedir, langs)
                except (IOError, OSError):
                    _LOGGER.error(
                    ("Cannot find translations for language '{}' in '{}' with "
                        "domain '{}'. Installing NullTranslations.").format(
                            langs[0], localedir, domain))
                    translations = gettext.NullTranslations()
            newstyle = generator.settings.get('I18N_GETTEXT_NEWSTYLE', True)
            generator.env.install_gettext_translations(translations, newstyle)

    def prepare_subsites_iterables(self):
        '''Prepare iterable variables to add to template context'''
        self.main_site_lang = self.main_settings['DEFAULT_LANG']
        main_siteurl = self.main_settings['SITEURL']
        self.main_siteurl = '/' if main_siteurl == '' else main_siteurl
        lang_siteurls = list(self.subsite_db.items())
        lang_siteurls.insert(0, (self.main_site_lang, main_siteurl))
        self._lang_siteurls = OrderedDict(lang_siteurls)

    def add_variables_to_context(self, generator):
        '''Adds useful iterable variables to template context'''
        context = generator.context             # minimize attr lookup
        context['content_db'] = self.content_db
        context['get_rel_to_siteulr'] = self.relative_to_siteurl
        context['main_siteurl'] = self.main_siteurl
        context['main_lang'] = self.main_site_lang
        context['lang_siteurls'] = self._lang_siteurls
        current_lang = generator.settings['DEFAULT_LANG']
        extra_siteurls = self._lang_siteurls.copy()
        extra_siteurls.pop(current_lang)
        context['extra_siteurls'] = extra_siteurls

    def interlink_translations(self, content):
        '''Link content to translations in their main language

        so the URL (including localized month names) of the different subsites
        will be honored
        '''
        for translation in content.translations:
            relurl = self.subsite_relurl_db[translation.lang]
            translation_raw = self.content_db[translation.source_path]
            translation.override_url = urljoin(relurl, translation_raw.url)

    def interlink_static_files(self, generator):
        '''Add links to static files in the main site if necessary'''
        filenames = generator.context['filenames'] # minimize attr lookup
        relurl = self.subsite_relurl_db[generator.settings['DEFAULT_LANG']]
        for staticfile in self.main_static_files:
            if staticfile.source_path not in filenames:
                staticfile = copy(staticfile) # prevent override in main site
                staticfile.override_url = urljoin(relurl, staticfile.url)
                filenames[staticfile.source_path] = staticfile

    def save_main_static_files(self, static_generator):
        if static_generator.settings == self.main_settings:
            self.main_static_files = static_generator.staticfiles

    def update_generators(self):
        '''Update the context of all generators

        Ads useful variables and translations into the template context
        and interlink translations
        '''
        self.prepare_subsites_iterables()

        for generator in self.generators:
            contents, other_contents, _ = _get_contents_attrs(generator)
            for content in chain(contents, other_contents):
                self.interlink_translations(content)
            self.install_templates_translations(generator)
            self.add_variables_to_context(generator)
            self.interlink_static_files(generator)

    def get_next_subsite_settings(self):
        settings = self.main_settings.copy()
        lang, overrides = self.subsite_queue.popitem()
        settings.update(overrides)

        # to change what is perceived as translations
        settings['DEFAULT_LANG'] = lang

        # default subsite hierarchy
        if 'SITEURL' not in overrides:
            main_siteurl = self.main_siteurl
            main_siteurl = '/' if main_siteurl == '' else main_siteurl   #TODO make sure it works for both relative and absolute
            settings['SITEURL'] = main_siteurl + lang
        siteurl = settings['SITEURL']
        self.subsite_db[lang] = siteurl
        self.subsite_relurl_db[lang] = self.relative_to_siteurl(siteurl)
        if 'OUTPUT_PATH' not in overrides:
            settings['OUTPUT_PATH'] = os.path.join(
                self.main_settings['OUTPUT_PATH'], lang)
        if 'STATIC_PATHS' not in overrides:
            settings['STATIC_PATHS'] = []
        if 'THEME' in overrides:
            settings['THEME_STATIC_DIR'] = urljoin(self.subsite_relurl_db[lang],
                                        self.main_settings['THEME_STATIC_DIR'])
            settings['THEME_STATIC_PATHS'] = []

        settings = configure_settings(settings)      # to set LOCALE, etc.
        return settings

    @staticmethod
    def get_pelican_cls(settings):
        cls = settings['PELICAN_CLASS']
        if isinstance(cls, six.string_types):
            module, cls_name = cls.rsplit('.', 1)
            module = __import__(module)
            cls = getattr(module, cls_name)
        return cls

    def create_next_subsite(self, pelican_obj):
        '''Create the next subsite using the lang-specific config

        If there are no more subsites in the generation queue, update all
        the generators (interlink translations and add variables and
        translations to template context). Otherwise get the language and
        overrides for next the subsite in the queue and apply overrides,
        append language subpath to SITEURL and OUTPUT_PATH if they are not
        overriden. Then set DEFAULT_LANG to the language code to change
        perception of what is translated. Then generate the subsite using
        a PELICAN_CLASS instance and its run method. Finally, restore the
        previous locale.
        '''
        if len(self.subsite_queue) == 0:
            _LOGGER.debug('Updating cross-sub-site links for all generators.')
            self.update_generators()
            self.main_settings = None             # to initialize next time
        else:
            with temporary_locale():
                settings = self.get_next_subsite_settings()
                cls = self.get_pelican_cls(settings)

                new_pelican_obj = cls(settings)
                _LOGGER.debug(("Generating i18n subsite for lang '{}' "
                               "using class {}").format(
                                   settings['DEFAULT_LANG'], cls))
                new_pelican_obj.run()


def register():
    '''Create a SubsitesCreator instance and register it'''
    subsites_creator = SubsitesCreator()
    subsites_creator.register()
