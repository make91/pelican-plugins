'''Unit tests for the i18n_subsites plugin'''

import unittest
import i18n_subsites.i18n_subsites as i18ns
from pelican.generators import ArticlesGenerator
from pelican.tests.support import get_settings
from pelican import Pelican

import locale

class TestTemporaryLocale(unittest.TestCase):
    '''Test the temporary locale context manager'''

    def test_locale_restored(self):
        '''Test that the locale is restored after exiting context'''
        orig_locale = locale.setlocale(locale.LC_ALL)
        with i18ns.temporary_locale():
            locale.setlocale(locale.LC_ALL, 'C')
            self.assertEqual(locale.setlocale(locale.LC_ALL), 'C')
        self.assertEqual(locale.setlocale(locale.LC_ALL), orig_locale)

    def test_temp_locale_set(self):
        '''Test that the temporary locale is set'''
        with i18ns.temporary_locale('C'):
            self.assertEqual(locale.setlocale(locale.LC_ALL), 'C')


class TestGeneratorAttrs(unittest.TestCase):
    '''Test generator attributes getting and setting'''

    def setUp(self):
        '''Prepare a generator instance to test on'''
        self.generator = ArticlesGenerator(context={}, settings=get_settings(),
                                           path=None, theme='', output_path=None)

    def tearDown(self):
        '''Delete the generator'''
        del self.generator

    def test_get_attr_names(self):
        '''Test that the right attr names are returned for the generator'''
        self.assertEqual(i18ns._get_known_attrs_names(self.generator),
                         i18ns._GENERATOR_ATTRS[ArticlesGenerator])

    def test_get_attr_names_wrong_generator(self):
        '''Test that it fails on an unknown generator'''
        self.assertRaisesRegex(TypeError,
            ('Class <class \'object\'> of generator <object object at .*> is not '
            'supported by the i18n_subsites plugin \(relevant attribute names are '
            'not known\)'),
                               i18ns._get_known_attrs_names, object())

    def test_get_attrs(self):
        '''Test that the correct attributes are returned'''
        attrs = i18ns._get_contents_attrs(self.generator)
        attr_names = i18ns._GENERATOR_ATTRS[ArticlesGenerator][:2]
        for attr_name, attr in zip(attr_names, attrs):
            attr_gen = getattr(self.generator, attr_name)
            self.assertIs(attr, attr_gen)

    def test_set_attrs(self):
        '''Test that the correct attributes are set'''
        translations = [1, 2]
        drafts_translations = [3, 4]
        i18ns._set_translations_attrs(self.generator, translations, drafts_translations)
        self.assertIs(self.generator.translations, translations)
        self.assertIs(self.generator.drafts_translations, drafts_translations)


class TestSettingsManipulation(unittest.TestCase):
    '''Test operations on settings dict'''

    def setUp(self):
        '''Prepare default settings'''
        self.settings = get_settings()

    def test_disable_lang_variables(self):
        '''Test that *_LANG_* variables are disabled'''
        i18ns.disable_lang_variables(self.settings)
        self.assertEqual(self.settings['ARTICLE_LANG_URL'],
                         self.settings['ARTICLE_URL'])
        self.assertEqual(self.settings['PAGE_LANG_URL'],
                         self.settings['PAGE_URL'])
        self.assertEqual(self.settings['ARTICLE_LANG_SAVE_AS'],
                         self.settings['ARTICLE_SAVE_AS'])
        self.assertEqual(self.settings['PAGE_LANG_SAVE_AS'],
                         self.settings['PAGE_SAVE_AS'])

    def test_get_pelican_cls_class(self):
        '''Test that we get class given as an object'''
        self.settings['PELICAN_CLASS'] = object
        cls = i18ns.get_pelican_cls(self.settings)
        self.assertIs(cls, object)
        
    def test_get_pelican_cls_str(self):
        '''Test that we get correct class given by string'''
        cls = i18ns.get_pelican_cls(self.settings)
        self.assertIs(cls, Pelican)
        

class TestSitesRelpath(unittest.TestCase):
    '''Test relative path between sites generation'''

    def setUp(self):
        '''Generate some sample siteurls'''
        self.siteurl = 'http://example.com'
        i18ns._SITE_DB['en'] = self.siteurl
        i18ns._SITE_DB['de'] = self.siteurl + '/de'

    def tearDown(self):
        '''Remove sites from db'''
        i18ns._SITE_DB.clear()

    def test_get_site_path(self):
        '''Test getting the path within a site'''
        self.assertEqual(i18ns.get_site_path(self.siteurl), '/')
        self.assertEqual(i18ns.get_site_path(self.siteurl + '/de'), '/de')

    def test_relpath_to_site(self):
        '''Test getting relative paths between sites'''
        self.assertEqual(i18ns.relpath_to_site('en', 'de'), 'de')
        self.assertEqual(i18ns.relpath_to_site('de', 'en'), '..')

        
