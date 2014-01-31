"""Site i18n plugin creates i18n-ized copies of the default site"""



from pelican import signals, Pelican
import six



HIDE_UNTRANSLATED_POSTS = False


# Global vars
_translations = dict()
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
        pelican = Pelican(config)
        pelican.run()



def record_translations(content_object):
    """This function stores translations for content

    Translations are first removed from generation pipeline,
    their links are fixed to point to lang site copies
    and later added back only to generate translations links
    """
    global _translations, _main_site_generated
    if _main_site_generated:
        return
    _translations[content_object] = content_object.translations
    #content_object.translations = [] #TODO need to set them again somewhere to put them into templates and create translation links



def remove_generator_translations(generator, *args):
    """Empty the (hidden_)translation attribute of article and pages generators

    to prevent generating the translations as they will be generated in the lang sub-site
    """
    generator.translations = []
    if hasattr(generator, "hidden_translations"):
        generator.hidden_translations = []
        

def register():
    signals.finalized.connect(create_lang_copies)
    signals.content_object_init.connect(record_translations)
    signals.article_generator_finalized.connect(remove_generator_translations)
    signals.page_generator_finalized.connect(remove_generator_translations)
