# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.collection.testing import \
    PLONEAPPCOLLECTION_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, setRoles, login


class PloneAppCollectionClassTest(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.types = self.portal.portal_types

    def test_css_registered(self):
        cssreg = getattr(self.portal, 'portal_css')
        stylesheets_ids = cssreg.getResourceIds()
        self.failUnless(
            '++resource++plone.app.collection.css' in stylesheets_ids)

    def test_atcontenttypes_replaced_by_dexterity_types(self):
        self.assertEquals(self.types['Collection'].meta_type, 'Dexterity FTI')
