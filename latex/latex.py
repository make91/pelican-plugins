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
import re
from tempfile import mkdtemp
from shutil import rmtree
import subprocess as sp

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open


# configuration file for tex4ht that makes it output only body contents
_DEFAULT_TEX4HT_CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pelican_tex4ht')
# metadata fields regexp
_METADATA_REGEXP = re.compile(r'%metadata (?P<key>.*): (?P<value>.*)',
                             re.UNICODE | re.DOTALL | re.IGNORECASE)
_META_MACROS_REGEXP = re.compile(r'\\(?P<key>author|date|title)\{(?P<value>.*?)\}',
                                re.UNICODE | re.DOTALL | re.IGNORECASE)


class TeXReader(BaseReader):
    """Reads *.tex files (including LaTeX) using the tex4ht suite

    which transforms them into HTML files (only the body contents are used)
    """
    enabled = True
    file_extensions = ['tex']

    def __init__(self, *args, **kwargs):
        """Initialize reader and get compiler settings"""
        super(TeXReader, self).__init__(*args, **kwargs)
        self.compiler = self.settings.get('MK4HT_COMPILER', 'htlatex')
        self.compiler_cfg = self.settings.get('MK4HT_COMPILER_CFG', _DEFAULT_TEX4HT_CFG)
        self.compiler_opts = self.settings.get('MK4HT_COMPILER_OPTS', 'mathml,-css,NoFonts,charset=utf8')
        self.tex4ht_opts = self.settings.get('TEX4HT_OPTS', ' -cunihtf -utf8') #notice the space
        self.t4ht_opts = self.settings.get('T4HT_OPTS', '')

    def compile_content(self, filename):
        """Compile HTML body contents using mk4ht"""
        temp_dir = mkdtemp()
        try:
            devnull = sp.DEVNULL          # NOQA
        except AttributeError:                   # py2k
            devnull = open(os.devnull, 'wb')
        process = sp.Popen(['mk4ht', self.compiler, filename,
                            self.compiler_cfg + ',' + self.compiler_opts,
                            self.tex4ht_opts,
                            self.t4ht_opts,
                            ],
                            stdout=devnull,
                            stderr=devnull,
                            cwd=temp_dir,
            )
        exit_code = process.wait()
        if exit_code != 0:
            raise RuntimeError('mk4ht exited with code {},\nfull log: {}'.format(exit_code,
                      os.path.join(temp_dir, os.path.basename(filename).replace('.tex', '.log'))
                      ))

        html_output = os.path.join(temp_dir, os.path.basename(filename).replace('.tex', '.html'))
        with pelican_open(html_output) as raw_content:
            content = raw_content.strip() # remove extra whitespace
        
        # clean up
        rmtree(temp_dir)

        return content

    def extract_metadata(self, filename):
        """Extract metadata from comments and common macros in source file"""
        with pelican_open(filename) as source:
            metadata = dict(match.groups() for match in _METADATA_REGEXP.finditer(source) if match is not None)
            metadata.update(match.groups() for match in _META_MACROS_REGEXP.finditer(source) if match is not None)
            for key, value in metadata.items():
                metadata[key] = self.process_metadata(key, value)

        return metadata

    def read(self, filename):
        """Let tex4ht create a HTML body contents and parse the *.tex file for metadata"""
        return self.compile_content(filename), self.extract_metadata(filename)


def add_reader(readers):
    """Register the TeXReader"""
    readers.reader_classes['tex'] = TeXReader

    
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
