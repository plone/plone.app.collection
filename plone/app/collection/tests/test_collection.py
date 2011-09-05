# -*- coding: utf-8 -*-
from Acquisition import aq_inner

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.collection.testing import \
    PLONEAPPCOLLECTION_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, setRoles, login

from plone.app.collection.interfaces import ICollection

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]

#query = [{
#    'i': 'SearchableText',
#    'o': 'plone.app.querystring.operation.string.contains',
#    'v': 'Autoren'
#}]


class PloneAppCollectionIntegrationTest(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, 
                           name='Collection')
        schema = fti.lookupSchema()
        self.assertEquals(ICollection, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, 
                           name='Collection')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, 
                           name='Collection')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ICollection.providedBy(new_object))

    def test_adding(self):
        self.folder.invokeFactory('Collection', 
                                  'collection1')
        p1 = self.folder['collection1']
        self.failUnless(ICollection.providedBy(p1))


class PloneAppCollectionViewsTest(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Collection', 
                                  'collection1')
        self.collection = aq_inner(self.folder['collection1'])

    def test_view(self):
        view = self.collection.restrictedTraverse('@@view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

    def test_standard_view(self):
        view = self.collection.restrictedTraverse('standard_view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

    def test_summary_view(self):
        view = self.collection.restrictedTraverse('summary_view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

    def test_all_content(self):
        view = self.collection.restrictedTraverse('all_content')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

    def test_tabular_view(self):
        view = self.collection.restrictedTraverse('tabular_view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

    def test_thumbnail_view(self):
        view = self.collection.restrictedTraverse('thumbnail_view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
