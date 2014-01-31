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
    global _translations
    _translations[content_object] = content_object.translations
    #content_object.translations = [] #TODO need to set them again somewhere to put them into templates and create translation links



def register():
    signals.finalized.connect(create_lang_copies)
    signals.content_object_init.connect(record_translations)
