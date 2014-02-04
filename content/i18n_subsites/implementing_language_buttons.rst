-----------------------------
Implementing language buttons
-----------------------------
:date: 2014-02-03
:slug: implementing-lang-buttons
:lang: en

Each article with translations has translations links, but that's the only way to switch between language subsites.

I wanted to make it simple to switch between the language subsites on all pages, so I decided to add language buttons to the top menu bar.

For this purpose I used the ``extra_siteurls`` dictionary exported by the ``i18n_subsites`` plugin into the template context. This dictionary maps the language code to the SITEURL of the respective subsite. But I wanted the language button to show the names of the language codes, not just the language codes.

Perhaps I should have added support for putting the names in ``I18N_SUBSITES`` and exporting the names in ``extra_siteurls`` too? No, I want to keep the ``i18n_subsites`` plugin as simple as possible and let people add features onto it. IMHO that is better than making many assumptions about what people may want, because you cannot please everyone, e.g. somebody would rather put there flags [#flags]_.

So, the (IMHO) simplest way to support this is to make a simple jinja2 filter that translates the language code to the language name via a dictionary. Here is the relevant part of my pelicanconf.py

.. code-block:: python

   languages_lookup = {
		'en': 'English',
		'cz': 'Čeština',
		}

   def lookup_lang_name(lang_code):
       return languages_lookup[lang_code]

   JINJA_FILTERS = {
		'lookup_lang_name': lookup_lang_name,
		}

Now it's just a matter of using the filter in the ``base.html`` template at the beginning of the navbar

.. code-block:: jinja

   <!-- SNIP -->
   <nav><ul>
   {% if extra_siteurls %}
   {% for lang, url in extra_siteurls.items() %}
   <li><a href="{{ url }}">{{ lang | lookup_lang_name }}</a></li>
   {% endfor %}
   {% endif %}
   <!-- separator -->
   <li style="background-color: white; padding: 5px;">&nbsp</li>
   {% for title, link in MENUITEMS %}
   <!-- SNIP -->

You can see the result for yourself at the top of the page.

.. [#flags] Although it may look nice, `w3 discourages it <http://www.w3.org/TR/i18n-html-tech-lang/#ri20040808.173208643>`_.
