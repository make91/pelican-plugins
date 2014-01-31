Site i18n plugin
================

This plugin creates i8n-ized site copies for the default site. It extends the translations functionality.
Thus it is somewhat redundant with the *\*_LANG_SAVE_AS* variables.

How it works
------------
1. During building the site for *DEFAULT_LANG* the translations are not generated, but their relation to articles is kept.
2. For each non-default language a "sub-site" with a specified config[#conf]_ is created[#run]_, linking the translations to the originals (if available).

Content without a translation for a language is generated if the *HIDE_UNTRANSLATED_CONTENT* variable is False.

.. [#conf] for each language a config is given in the *I18N_CONFIGS* dictionary, it is imported as ``pelicanconf`` so your ``publishconf`` will use it too
.. [#run] using a new ``pelican.Pelican`` object

Setting it up
-------------

For each extra used language a different *pelicanconf.py* must be given (either path or module) in the *I18N_CONFIGS* dictionary

    I18N_CONFIGS = {
        'cz': 'pelicanconf_cz.py'
	}

The i18n-ized config may specify a different *LOCALE*, *SITENAME*, *TIMEZONE*, etc.
Most importantly, it **must** specify a different *OUTPUT_PATH* and *SITEURL*, e.g.

    OUTPUT_PATH = 'output/cz/'
    SITEURL = 'http://mysite.com/cz'

*RELATIVE_URLS* may have to be False too

Lastly, you should specify a localized theme that you translated to your liking. 
It is also convenient to add language buttons to your theme in addition to the translations links.


Future plans
------------
- Instead of specifying a different theme for each language, the ``jinja2.ext.i18n`` extension could be used.
