# -*- coding: utf-8 -*-
"""
Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.
"""


import os
from tempfile import mkdtemp, mkstemp
from shutil import rmtree
import subprocess as sp

from pelican import signals
from pelican.readers import HTMLReader


class Tex4htReader(HTMLReader):
    """Reads *.tex files (including LaTeX) using tex4ht

    which transforms them into HTML files,
    which are then read by the standard HTMLReader
    """
    enabled = True
    file_extensions = ['tex']

    def _make_cfg(self, temp_dir):
        """Create a configuration file for tex4ht

        this includes various metadata fields
        """
        fd , cfg_file = mkstemp(suffix='.cfg', dir=temp_dir)
        f = os.fdopen(fd)
        f.write("""\Preamble{html}
        \def\tags#1{\gdef\@tags{#1}}
        \def\category#1{\gdef\@category{#1}}
        \def\summary#1{\gdef\@summary{#1}}
        \def\modified#1{\gdef\@modified{#1}}
        \Configure{TITLE+}{\@title}
        \begin{document}
        \HCode{<meta name="author" content="}\@author\HCode{" />}
        \HCode{<meta name="author" content="}\@date\HCode{" />}
        \HCode{<meta name="tags" content="}\@tags\HCode{" />}
        \HCode{<meta name="category" content="}\@category\HCode{" />}
        \HCode{<meta name="summary" content="}\@summary\HCode{" />}
        \HCode{<meta name="summary" content="}\@modified\HCode{" />}
        \EndPreamble
        """)
        f.close()
        return cfg_file[:-4]                            # without .cfg
                  
    def read(self, filename):
        """Let tex4ht create a HTML file and then parse it"""
        temp_dir = mkdtemp()
        cfg_file = self._make_cfg(temp_dir)
        process = sp.Popen(['mk4ht', 'htlatex', filename,
                            cfg_file + ',mathml,-css,NoFonts,charset=utf8',
                            '-utf8',
                            #'-d' + output_dir  # would only copy
                            ],
                            stdout=sp.DEVNULL,
                            stderr=sp.DEVNULL,
                            cwd=temp_dir,
            )
        process.wait()

        html_output = os.path.join(temp_dir, filename.replace('.tex', '.html'))
        content, metadata = super(Tex4htReader, self).read(html_output)  # parse the HTML
        
        # clean up
        rmtree(temp_dir)

        return content, metadata


def add_reader(readers):
    """Register the Tex4htReader"""
    readers.reader_classes['tex'] = Tex4htReader

    
# Reference about dynamic loading of MathJax can be found at http://docs.mathjax.org/en/latest/dynamic.html
# The https cdn address can be found at http://www.mathjax.org/resources/faqs/#problem-https
latexScript = """
    <script type= "text/javascript">
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.src = 'https:' == document.location.protocol ? 'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js' : 'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'; 
        s[(window.opera ? "innerHTML" : "text")] =
            "MathJax.Hub.Config({" + 
            "    config: ['MMLorHTML.js']," + 
            "    jax: ['input/TeX','input/MathML','output/HTML-CSS','output/NativeMML']," +
            "    TeX: { extensions: ['AMSmath.js','AMSsymbols.js','noErrors.js','noUndefined.js'], equationNumbers: { autoNumber: 'AMS' } }," + 
            "    extensions: ['tex2jax.js','mml2jax.js','MathMenu.js','MathZoom.js']," +
            "    tex2jax: { " +
            "        inlineMath: [ [\'$\',\'$\'] ], " +
            "        displayMath: [ [\'$$\',\'$$\'] ]," +
            "        processEscapes: true }, " +
            "    'HTML-CSS': { " +
            "        styles: { '.MathJax .mo, .MathJax .mi': {color: 'black ! important'}} " +
            "    } " +
            "}); ";
        (document.body || document.getElementsByTagName('head')[0]).appendChild(s);
    </script>
"""

def addLatex(gen, metadata):
    """
        The registered handler for the latex plugin. It will add 
        the latex script to the article metadata
    """
    if 'LATEX' in gen.settings.keys() and gen.settings['LATEX'] == 'article':
        if 'latex' in metadata.keys():
            metadata['latex'] = latexScript
    else:
        metadata['latex'] = latexScript

def register():
    """
        Plugin registration
    """
    signals.readers_init.connect(add_reader)
    signals.article_generator_context.connect(addLatex)
    signals.page_generator_context.connect(addLatex)
