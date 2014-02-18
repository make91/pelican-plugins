Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.

Installation
------------

To enable, ensure that `latex.py` is put somewhere that is accessible.
Then use as follows by adding the following to your settings.py:

    PLUGINS = ["latex"]

Be careful: Not loading the plugin is easy to do, and difficult to detect. To
make life easier, find where pelican is installed, and then copy the plugin
there. An easy way to find where pelican is installed is to verbose list the
available themes by typing `pelican-themes -l -v`. 

Once the pelican folder is found, copy `latex.py` to the `plugins` folder. Then 
add to settings.py like this:

    PLUGINS = ["pelican.plugins.latex"]

Now all that is left to do is to embed the following to your template file 
between the `<head>` parameters (for the NotMyIdea template, this file is base.html)

    {% if article and article.latex %}
        {{ article.latex }}
    {% endif %}
    {% if page and page.latex %}
        {{ page.latex }}
    {% endif %}

This plugin also installs the `TeXReader` which can read most (La)TeX files
with a file extension `*.tex`.

Usage
-----
Latex will be embedded in every article. If however you want latex only for
selected articles, then in settings.py, add

    LATEX = 'article'

And in each article, add the metadata key `latex:`. For example, with the above
settings, creating an article that I want to render latex math, I would just 
include 'Latex' as part of the metadata without any value:

    Date: 1 sep 2012
    Status: draft
    Latex:

###TeXReader usage

####Metadata in (La)TeX files

Arbitrary metadata can be specified in comments in this form

    %metadata tags: awesome,fun
    %metadata lang: en
    %metadata category: math

Additionally, the information defined by the standard macros

    \title{}
    \author{}
    \date{}

is also used as metadata.

####Tex4ht configuration

The `TeXReader` uses the `tex4ht` suite to compile (La)TeX into HTML files.
You can configure arguments to the `mk4ht` command using config variables used
in the `TeXReader.__init__` method. Alter them only if you know what you are doing!

Latex Examples
--------------
###Inline
Latex between `$`..`$`, for example, `$`x^2`$`, will be rendered inline 
with respect to the current html block.

###Displayed Math
Latex between `$$`..`$$`, for example, `$$`x^2`$$`, will be rendered centered in a 
new paragraph.

###Equations
Latex between `\begin` and `\end`, for example, `begin{equation}` x^2 `\end{equation}`, 
will be rendered centered in a new paragraph with a right justified equation number 
at the top of the paragraph. This equation number can be referenced in the document. 
To do this, use a `label` inside of the equation format and then refer to that label 
using `ref`. For example: `begin{equation}` `\label{eq}` X^2 `\end{equation}`. Now 
refer to that equation number by `$`\ref{eq}`$`.
   
Template And Article Examples
-----------------------------
To see an example of this plugin in action, look at 
[this article](http://doctrina.org/How-RSA-Works-With-Examples.html). To see how 
this plugin works with a template, look at 
[this template](https://github.com/barrysteyn/pelican_theme-personal_blog).
