==========================
 LaTeX Reader For Pelican
==========================

This plugin installs the ``TeXReader`` reader class which can read most 
(La)TeX files with the ``*.tex`` file extension. It is able to process
almost any macro, e.g. `\input{}` or `\ref{}`.

Requirements
------------

TeX4ht suite
............

The reader uses the `TeX4ht converter suite <http://www.tug.org/tex4ht/>`_
to convert (La)TeX files to HTML. This suite uses a real (la)tex compiler
under the hood, so it is best to install it as a part of a (La)TeX distribution
like `TeX Live <https://www.tug.org/texlive/>`_ or `MiKTeX <http://miktex.org/>`_.

The ``mk4ht`` command from that suite must be in ``PATH``.

MathJax (optional)
..................

The reader renders math as `MathML <http://en.wikipedia.org/wiki/MathML>`_ by default.
To render MathML more nicely and consistently across most browsers, 
`MathJax <http://www.mathjax.org/>`_ JavaScript engine may be used. It can be loaded by theme
templates as a `script from the MathJax CDN <http://docs.mathjax.org/en/latest/start.html#mathjax-cdn>`_.

The `latex Pelican plugin <https://github.com/getpelican/pelican-plugins/tree/master/latex>`_ 
will load MathJax automatically whenever MathML code is detected and will also ensure Typogrify 
will not interfere.

Installation
------------

The plugin can be installed as described in the `Pelican plugin framework documentation <http://docs.getpelican.com/en/latest/plugins.html>`_.

Usage
-----

Metadata in (La)TeX files
.........................

Arbitrary metadata can be specified in comments in this form, one per line

.. code-block:: latex

    %metadata tags: awesome,fun
    %metadata lang: en
    %metadata category: math

Additionally, the information defined by the standard macros

.. code-block:: latex

    \title{}
    \author{}
    \date{}

is also used as metadata.

\input{}, \include* macros
..........................

Any macros that search for content with a given path are instructed
by the ``TEXINPUTS`` environment variable to search in

1. the directory where the currently processed content is
2. the main content directory (pelican setting ``PATH``)

so any path given to macros may be relative to one of these directories.

However, the path must not start with ``./`` or ``../``, 
i.e. ``../data.texinput`` will not work.

Images
......

The ``\includegrephics{}`` macro used for images inclusion will look 
for image files in the same way that ``\input{}`` does. The optional
``width`` parameters is recognized too, but beware, the given dimension 
is translated to points (``pt``).

TeX4ht configuration
....................

You can configure arguments to the ``mk4ht`` command using config variables used
in the ``TeXReader.__init__`` method. Alter them only if you know what you are doing!

Known issues
------------

1. It is quite slow
...................

The reader is only as fast as the (la)tex compiler used under the hood.
That is the price for having full (La)TeX support.

2. HTML content contains a <style> tag and lots of CSS
......................................................

The TeX4ht suite relies on CSS to render content as close as possible
to the (La)TeX output. The ``<style>`` tag has a `scoped
<http://www.w3schools.com/tags/att_style_scoped.asp>`_ attribute, so
in browsers that support it, only the desired content will be
affected. However, it is unlikely that the unconventional class names
used by TeX4ht will interfere with the CSS used by the theme. If you
know a better solution, file an issue.

Future plans
------------
- images support
    - extensions management
    - dimensions, scale management - provide bounding box info
    - converting of eps -> would also enable bitmap math
- Bib(La)Tex support
    - select which backend to use
    - modify build process to run bib(la)tex after running latex

