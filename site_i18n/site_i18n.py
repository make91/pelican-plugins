"""Site i18n plugin creates i18n-ized copies of the default site"""



import six

from pelican import signals, Pelican
import pelican.settings



HIDE_UNTRANSLATED_POSTS = False


# Global vars
_main_site_generated = False



def create_lang_copies(pelican):
    global _main_site_generated
    if _main_site_generated:
        return
    else:
        _main_site_generated = True
    for lang, config in I18N_CONFIGS.items():
        if not isinstance(config, six.types.ModuleType):
            try:
                config = __import__(config)
            except ImportError:
                print("Cannot import config '{}' for lang '{}', skipping".format(str(config), lang))
                continue
        # TODO put the module in place of pelicanconf
        settings = pelican.settings.get_settings_from_module(config)
        pelican = Pelican(settings)
        pelican.run()



def move_translations(content_object):
    """This function points translations links to the sub-sites

    by prepending their location with the language code
    """
    if _main_site_generated:
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
    signals.finalized.connect(create_lang_copies)
    signals.content_object_init.connect(move_translations)
    signals.article_generator_finalized.connect(remove_generator_translations)
    signals.page_generator_finalized.connect(remove_generator_translations)
