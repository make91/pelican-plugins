i18n subsites plugin
===================

This plugin extends the translations functionality by creating i8n-ized sub-sites for the default site.
It is therefore redundant with the *\*_LANG_{SAVE_AS,URL}* variables, so it disables them to prevent conflicts.

What it does
------------
1. The *\*_LANG_URL* and *\*_LANG_SAVE_AS* variables are set to their normal counterparts (e.g. *ARTICLE_URL*) so they don't conflict with this scheme.
2. While building the site for *DEFAULT_LANG* the translations of pages and articles are not generated, but their relations to the original content is kept via links to them.
3. For each non-default language a "sub-site" with a specified config [#conf]_ is created [#run]_, linking the translations to the originals (if available). The language code used is appended to the *OUTPUT_PATH* and *SITE_URL* of each sub-site.

If *HIDE_UNTRANSLATED_CONTENT* is True (default), content without a translation for a language is generated as hidden (for pages) or draft (for articles) for the corresponding language sub-site.

.. [#conf] for each language a config is given in the *I18N_CONF_OVERRIDES* dictionary
.. [#run] using a new ``pelican.Pelican`` object and its ``pelican.Pelican.run`` method

Setting it up
-------------

For each extra used language a different *pelicanconf.py* must be given (as a relative path) in the *I18N_CONF_OVERRIDES* dictionary::

    PLUGINS = ['i18n_subsites', ...]

    # mapping: language_code -> path_to_conf_override
    I18N_CONF_OVERRIDES = {
        'cz': 'pelicanconf_cz.py'
	}

The i18n-ized config may specify configuration variable overrides, e.g. a different *LOCALE*, *SITENAME*, *TIMEZONE*, etc. 
However, it should not override *OUTPUT_PATH* and *SITEURL* as they are modified automatically by appending the language code.
Most importantly, a localized [#local]_ theme can be specified in *THEME*.

Note that the variables specified in these overriding configs only update those given in the config file given to pelican.
This means that *publishconf.py* will work as expected.

.. [#local] It is convenient to add language buttons to your theme in addition to the translations links.

Usage notes
-----------
- It is mandatory to specify *lang* metadata for each article and page as *DEFAULT_LANG* is later changed for each sub-site.
- As with the original translations functionality, *slug* metadata is used to group translations. It is therefore often
  convenient to compensate for this by overriding the content url (which defaults to slug) using the *url* and *save_as* metadata.

Future plans
------------
- Find a better way of loading the config overrides that doesn't reinitialize so many vars.
- Instead of specifying a different theme for each language, the ``jinja2.ext.i18n`` extension could be used. 
  This would require some gettext and babel infrastructure.

Development
-----------
Please file issues, pull requests at https://github.com/smartass101/pelican-plugins
