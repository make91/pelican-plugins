"""Site i18n plugin creates i18n-ized subsites of the default site"""



import os
import logging
from itertools import chain

from pelican import signals, Pelican
from pelican.settings import read_settings
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

    append language code to SITEURL and OUTPUT_PATH for each generated lang"""
    global _main_site_generated, _main_site_root, _main_site_lang
    if _main_site_generated:
        return
    else:
        _main_site_generated = True

    orig_settings = pelican_obj.settings.copy()
    _main_site_root = orig_settings['SITEURL']
    _main_site_lang = orig_settings['DEFAULT_LANG']
    for lang, config_path in pelican_obj.settings.get('I18N_CONF_OVERRIDES', {}).items():
        try:
            overrides = read_settings(config_path)
        except Exception:
            logging.error("Cannot read config overrides '{}' for lang '{}', skipping.".format(config_path, lang))
            continue
        settings = orig_settings.copy()
        settings.update(overrides)
        settings['PATH'] = orig_settings['PATH']   #it got reinitialized
        settings['SITEURL'] = _main_site_root + '/' + lang
        settings['OUTPUT_PATH'] = os.path.join(settings['OUTPUT_PATH'], lang, '')
        settings['DEFAULT_LANG'] = lang   #to change what is perceived as translations
        settings['DELETE_OUTPUT_DIRECTORY'] = False
        pelican_obj = Pelican(settings)   #TODO use PELICAN_CLASS
        pelican_obj.run()



def hide_untranslated_content(generator, *args):
    """Hide content without translation for current DEFAULT_LANG

    if HIDE_UNTRANSLATED_CONTENT is True
    """
    if not generator.settings.get('HIDE_UNTRANSLATED_CONTENT', True):
        return
    is_pages_gen = hasattr(generator, 'pages')
    contents = generator.pages if is_pages_gen else generator.articles
    hidden_contenets = generator.hidden_pages if is_pages_gen else generator.drafts 
    print(contents)
    default_lang = generator.settings['DEFAULT_LANG']
    for content_object in contents:
        print(content_object.lang, default_lang)
        if content_object.lang != default_lang:
            if isinstance(content_object, Page):
                content_object.status = 'hidden'
            elif isinstance(content_object, Article):
                content_object.status = 'draft'        
            contents.remove(content_object)
            hidden_contenets.append(content_object)


            
def move_translations_links(content_object):
    """This function points translations links to the sub-sites

    by prepending their location with the language code
    or directs a DEFAULT_LANG translation back to top level site
    """
    for translation in content_object.translations:
        if translation.lang == _main_site_lang:
        # cannot prepend, must take to top level
            lang_prepend = '../'
        else:
            lang_prepend = translation.lang + '/'
        translation.override_url =  lang_prepend + translation.url



def update_generator_translations(generator, *args):
    """Empty the (hidden_)translation attribute of article and pages generators

    to prevent generating the translations as they will be generated in the lang sub-site
    also point the translations links to the sub-sites
    """
    generator.translations = []
    if hasattr(generator, "hidden_translations"): # must be a page generator
        generator.hidden_translations = []
        for page in chain(generator.pages, generator.hidden_pages):
            move_translations_links(page)
    else:                                    # is an article generator
        for article in chain(generator.articles, generator.drafts):
            move_translations_links(article)



def register():
    signals.initialized.connect(disable_lang_vars)
    signals.finalized.connect(create_lang_subsites)
    signals.article_generator_finalized.connect(hide_untranslated_content)
    signals.page_generator_finalized.connect(hide_untranslated_content)
    signals.article_generator_finalized.connect(update_generator_translations)
    signals.page_generator_finalized.connect(update_generator_translations)
