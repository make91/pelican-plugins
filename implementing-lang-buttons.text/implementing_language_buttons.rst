-----------------------------
Implementing language buttons
-----------------------------
:date: 2014-02-03
:slug: implementing-lang-buttons
:lang: en

Each article with translations has translations links, but that's the only way to switch between language subsites.

I wanted to make it simple to switch between the language subsites on all pages, so I decided to add language buttons to the top menu bar.

For this purpose I used the ``extra_siteurls`` dictionary exported by the ``i18n_subsites`` plugin into the template context. This dictionary maps the language code to the SITEURL of the respective subsite. But I wanted the language button to show the names of the languages, not just the language codes.

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
   <!-- separator -->
   <li style="background-color: white; padding: 5px;">&nbsp</li>
   {% endif %}
   {% for title, link in MENUITEMS %}
   <!-- SNIP -->


Different design
----------------

Later I decided that I want to show the active language in the navbar too
.
So, I needed a list of all the languages the site supports, so I used the *I18N_SUBSITES* dictionary as it is available in templates (because it is an all-caps config setting) and extracted the list of languages as ``I18N_SUBSITES.keys()``.

Here is the slightly modified template

.. code-block:: jinja

   <!-- SNIP -->
   <nav><ul>
   {% if extra_siteurls and I18N_SUBSITES %}
   {% for lang in [main_lang] + (I18N_SUBSITES.keys() | list) %}
   <li{% if lang == DEFAULT_LANG %} class="active"{% endif %}><a href="{{ extra_siteurls.get(lang, SITEURL) }}">{{ lang | lookup_lang_name }}</a></li>
   {% endfor %}
   <!-- separator -->
   <li style="background-color: white; padding: 5px;">&nbsp</li>
   {% endif %}
   {% for title, link in MENUITEMS %}
   <!-- SNIP -->

What it does:

1. get a list of all languages as the main language (``main_lang`` exported by the ``i18n_subsites`` plugin) and the subsites languages. The list filter is needed as ``keys()`` does not return a list and the list concatenation (``+``) would not work
2. for each lang it makes link and makes it active if it is the *DEFAULT_LANG* of the currently rendered subsite
3. gets the url for the (sub)site. If the lang is not in ``extra_siteurls``, it must be the current *DEFAULT_LANG*, so use the current *SITEURL*
4. looks up the language name

You can see the result for yourself at the top of the page.

Now that I look at the above snippet, I'm not sure if ``extra_siteurls`` is that convenient. Perhaps something like ``lang_siteurls`` dictionary for all languages would have been more convenient. Anyways, all the information is available in the context at the moment, if it bugs you too much, contact me and I'll improve it.

Update: added ``lang_siteurls`` for convenience' sake
-----------------------------------------------------

I decided that I want to make things as easy as possible for the user, so I implemented ``lang_siteurls``. 

So now I use this in my template

.. code-block:: jinja

   <!-- SNIP -->
   <nav><ul>
   {% if lang_siteurls %}
   {% for lang, siteurl in lang_siteurls.items() %}
   <li{% if lang == DEFAULT_LANG %} class="active"{% endif %}><a href="{{ siteurl }}">{{ lang | lookup_lang_name }}</a></li>
   {% endfor %}
   <!-- separator -->
   <li style="background-color: white; padding: 5px;">&nbsp</li>
   {% endif %}
   {% for title, link in MENUITEMS %}
   <!-- SNIP -->

Much nicer, don't you think? ;)

I also implemented ``lang_siteurls`` and ``extra_siteurls`` as an ``OrderedDict`` so that ``main_lang`` is always first. This also means that you can change the ordering of the dict through some jinja filter function like this in your config

.. code-block:: python

   def my_ordered_items(ordered_dict):
       items = list(ordered_dict.items())
       # swap first and last using tuple unpacking
       items[0], items[-1] = items[-1], items[0]
       return items

   JINJA_FILTERS = {
		...
		'my_ordered_items': my_ordered_items,
		}

And then the ``for`` loop line in the template becomes

.. code-block:: jinja

   <!-- SNIP -->
   {% for lang, siteurl in lang_siteurls | my_ordered_items %}
   <!-- SNIP -->


.. [#flags] Although it may look nice, `w3 discourages it <http://www.w3.org/TR/i18n-html-tech-lang/#ri20040808.173208643>`_.
