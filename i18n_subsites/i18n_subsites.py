"""Site i18n plugin creates i18n-ized subsites of the default site"""



import os
import six
import logging
from itertools import chain

from pelican import signals, Pelican
from pelican.contents import Page, Article


# Global vars
_main_site_generated = False
_main_site_root = ""
_main_site_lang = "en"
logger = logging.getLogger(__name__)



def disable_lang_vars(pelican_obj):
    """Set lang specific url and save_as vars to the non-lang defaults

    e.g. ARTICLE_LANG_URL = ARTICLE_URL
    They would conflict with this plugin otherwise
    """
    s = pelican_obj.settings
    for content in ['ARTICLE', 'PAGE']:
        for meta in ['_URL', '_SAVE_AS']:
            s[content + '_LANG' + meta] = s[content + meta]



def create_lang_subsites(pelican_obj):
    """For each language create a subsite using the lang-specific config

    for each generated lang append language subpath to SITEURL and OUTPUT_PATH
    and set DEFAULT_LANG to the language code to change perception of what is translated
    and set DELETE_OUTPUT_DIRECTORY to False to prevent deleting output from previous runs
    Then generate the subsite using a PELICAN_CLASS instance and its run method.
    """
    global _main_site_generated, _main_site_root, _main_site_lang
    if _main_site_generated:
        return
    else:
        _main_site_generated = True

    orig_settings = pelican_obj.settings
    _main_site_root = orig_settings['SITEURL']
    _main_site_lang = orig_settings['DEFAULT_LANG']
    for lang, overrides in orig_settings.get('I18N_SUBSITES', {}).items():
        settings = orig_settings.copy()
        settings.update(overrides)
        settings['SITEURL'] = _main_site_root + '/' + lang
        settings['OUTPUT_PATH'] = os.path.join(settings['OUTPUT_PATH'], lang, '')
        settings['DEFAULT_LANG'] = lang   # to change what is perceived as translations
        settings['DELETE_OUTPUT_DIRECTORY'] = False # prevent deletion of previous runs
        
        cls = settings['PELICAN_CLASS']
        if isinstance(cls, six.string_types):
            module, cls_name = cls.rsplit('.', 1)
            module = __import__(module)
            cls = getattr(module, cls_name)

        pelican_obj = cls(settings)
        logger.debug("Generating i18n subsite for lang '{}' using class '{}'".format(lang, str(cls)))
        pelican_obj.run()



def move_translations_links(content_object):
    """This function points translations links to the sub-sites

    by prepending their location with the language code
    or directs an original DEFAULT_LANG translation back to top level site
    """
    for translation in content_object.translations:
        if translation.lang == _main_site_lang:
        # cannot prepend, must take to top level
            lang_prepend = '../'
        else:
            lang_prepend = translation.lang + '/'
        translation.override_url =  lang_prepend + translation.url



def update_generator_contents(generator, *args):
    """Update the contents lists of a generator

    Empty the (hidden_)translation attribute of article and pages generators
    to prevent generating the translations as they will be generated in the lang sub-site
    and point the content translations links to the sub-sites

    Hide content without a translation for current DEFAULT_LANG
    if HIDE_UNTRANSLATED_CONTENT is True
    """
    generator.translations = []
    is_pages_gen = hasattr(generator, 'pages')
    if is_pages_gen:
        generator.hidden_translations = []
        for page in chain(generator.pages, generator.hidden_pages):
            move_translations_links(page)
    else:                                    # is an article generator
        for article in chain(generator.articles, generator.drafts):
            move_translations_links(article)
            
    if not generator.settings.get('HIDE_UNTRANSLATED_CONTENT', True):
        return
    contents = generator.pages if is_pages_gen else generator.articles
    hidden_contents = generator.hidden_pages if is_pages_gen else generator.drafts 
    default_lang = generator.settings['DEFAULT_LANG']
    for content_object in contents:
        if content_object.lang != default_lang:
            if isinstance(content_object, Page):
                content_object.status = 'hidden'
            elif isinstance(content_object, Article):
                content_object.status = 'draft'        
            contents.remove(content_object)
            hidden_contents.append(content_object)



def register():
    signals.initialized.connect(disable_lang_vars)
    signals.article_generator_finalized.connect(update_generator_contents)
    signals.page_generator_finalized.connect(update_generator_contents)
    signals.finalized.connect(create_lang_subsites)
