"""Site i18n plugin creates i18n-ized copies of the default site"""



from pelican import signals, Pelican
import six



HIDE_UNTRANSLATED_POSTS = False



def create_lang_copies(pelican):
    for lang, config in I18N_CONFIGS.items():
        if not isinstance(config, six.types.ModuleType):
            try:
                config = __import__(config)
            except ImportError:
                print("Cannot import config '{}' for lang '{}', skipping".format(str(config), lang))
                continue
        pelican = Pelican(config)
        pelican.run()


        
def register():
    signals.finalized.connect(create_lang_copies)
