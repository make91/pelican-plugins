# -*- coding: utf-8 -*-
"""==========================
 LaTeX Reader For Pelican
==========================

This plugin installs the ``TeXReader`` reader class which can read most 
(La)TeX files with the ``*.tex`` file extension. It is able to process
almost any macro, e.g. `\input{}` or `\ref{}`.
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
_METADATA_REGEXP = re.compile(r'%metadata (?P<key>.*): (?P<value>.*)$',
                              re.UNICODE | re.IGNORECASE | re.MULTILINE)
_META_MACROS_REGEXP = re.compile(r'\\(?P<key>author|date|title)\{(?P<value>.*?(?:\{.*\})*?)\}',
                                 re.UNICODE | re.IGNORECASE | re.DOTALL)


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
        self.compiler_opts = self.settings.get('MK4HT_COMPILER_OPTS', 'mathml')
        self.tex4ht_opts = self.settings.get('TEX4HT_OPTS', ' -cunihtf -utf8') #notice the space
        self.t4ht_opts = self.settings.get('T4HT_OPTS', '')

    def compile_content(self, filename):
        """Compile HTML body contents using mk4ht"""
        temp_dir = mkdtemp()
        logfile = open(os.path.join(temp_dir, 'mk4ht_process.log'), 'w')
        os.environ['TEXINPUTS'] = '{file_dir}:{content_dir}:'.format(
            file_dir=os.path.dirname(filename),         # simulate CWD
            content_dir=os.path.abspath(self.settings['PATH']),
            )
        process = sp.Popen(['mk4ht', self.compiler, filename,
                            self.compiler_cfg + ',' + self.compiler_opts,
                            self.tex4ht_opts,
                            self.t4ht_opts,
                            ],
                            stdout=logfile,
                            stderr=logfile,
                            cwd=temp_dir,
                            env=os.environ,
            )
        process.wait()
        output_template = os.path.join(temp_dir, os.path.basename(filename).replace('.tex', '{}'))
        html_output = output_template.format('.html')
        if not os.path.isfile(html_output):
            raise RuntimeError('mk4ht did not produce HTML output,\nlogs: {}\n      {}'.format(
                output_template.format('.log'),
                logfile.name,
                      ))

        with pelican_open(html_output) as raw_content:
            content = raw_content.strip() # remove extra whitespace
        # prepend content with scoped css style info to render it properly
        with pelican_open(output_template.format('.css')) as css_output:
            content = '\n'.join([
            # <code> to fool typogrify and make it not process the css stuff
                '<div class="tex4ht-content">\n<style type="text/css" scoped>/*<code>*/',
                css_output,
                '/*</code>*/</style>',
                content,
                '</div>',
                ])

        # clean up
        rmtree(temp_dir)

        return content

    def extract_metadata(self, filename):
        """Extract metadata from comments and common metadata macros in source file"""
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


def register():
    """Plugin registration"""
    signals.readers_init.connect(add_reader)
