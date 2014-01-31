"""Site i18n plugin creates i18n-ized subsites of the default site"""



import six

from pelican import signals, Pelican
from pelican.settings import read_settings



HIDE_UNTRANSLATED_POSTS = False


# Global vars
_main_site_generated = False



def create_lang_subsites(pelican_obj):
    """For each language create a subsite using the lang-specific config"""
    global _main_site_generated
    if _main_site_generated:
        return
    else:
        _main_site_generated = True
    for lang, config_path in pelican_obj.settings.get('I18N_CONF_OVERRIDES', {}).items():
        try:
            settings = read_settings(config_path)
        except Exception:
            print("Cannot read config '{}' for lang '{}', skipping.".format(config_path, lang))
            continue
        pelican_obj = Pelican(settings)
        pelican_obj.run()



def move_translations(content_object):
    """This function points translations links to the sub-sites

    by prepending their location with the language code
    """
    if _main_site_generated: #TODO needed? maybe we shoudl change utl every time
        return
    for translation in content_object.translations:
        if translation.in_default_lang:   # cannot prepend
            continue
        # prepend with / to go right to the root
        translation.url = '/' + translation.lang + '/' + translation.url



def remove_generator_translations(generator, *args):
    """Empty the (hidden_)translation attribute of article and pages generators

    to prevent generating the translations as they will be generated in the lang sub-site
    """
    generator.translations = []
    if hasattr(generator, "hidden_translations"):
        generator.hidden_translations = []
        

        
def register():
    signals.finalized.connect(create_lang_subsites)
    signals.content_object_init.connect(move_translations)
    signals.article_generator_finalized.connect(remove_generator_translations)
    signals.page_generator_finalized.connect(remove_generator_translations)
