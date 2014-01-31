"""Site i18n plugin creates i18n-ized subsites of the default site"""



import os

from pelican import signals, Pelican
from pelican.settings import read_settings
from pelican.contents import Article, Page



HIDE_UNTRANSLATED_POSTS = False #TODO: just loop through articles/posts, remove those withotu translations


# Global vars
_main_site_generated = False
_main_site_root = ""



def create_lang_subsites(pelican_obj):
    """For each language create a subsite using the lang-specific config

    append language code to SITEURL and OUTPUT_PATH for each generated lang"""
    global _main_site_generated, _main_site_root
    if _main_site_generated:
        return
    else:
        _main_site_generated = True

    orig_settings = pelican_obj.settings.copy()
    _main_site_root = orig_settings['SITEURL']
    for lang, config_path in pelican_obj.settings.get('I18N_CONF_OVERRIDES', {}).items():
        try:
            overrides = read_settings(config_path)
        except Exception:
            print("Cannot read config overrides '{}' for lang '{}', skipping.".format(config_path, lang))
            continue
        settings = orig_settings.copy()
        settings.update(overrides)
        settings['SITEURL'] = settings['SITEURL'] + '/' + lang
        settings['OUTPUT_PATH'] = os.path.join(settings['OUTPUT_PATH'], lang, '')
        settings['DEFAULT_LANG'] = lang   #to change what is perceived as translations
        pelican_obj = Pelican(settings)
        pelican_obj.run()



def move_translations(content_type, content_object):
    """This function points translations links to the sub-sites

    by prepending their location with the language code
    """
    for translation in content_object.translations:
        if translation.in_default_lang:   # cannot prepend
            continue
        lang_prepend = translation.lang + '/'
        prepend = _main_site_root + '/' + lang_prepend if _main_site_root != '' else lang_prepend
        translation.override_url =  prepend + translation.url



def remove_generator_translations(generator, *args):
    """Empty the (hidden_)translation attribute of article and pages generators

    to prevent generating the translations as they will be generated in the lang sub-site
    """
    generator.translations = []
    if hasattr(generator, "hidden_translations"):   #must be a post
        generator.hidden_translations = []
        

        
def register():
    signals.finalized.connect(create_lang_subsites)
    signals.content_object_init.connect(move_translations, sender=Article)
    signals.content_object_init.connect(move_translations, sender=Page)
    signals.article_generator_finalized.connect(remove_generator_translations)
    signals.page_generator_finalized.connect(remove_generator_translations)
