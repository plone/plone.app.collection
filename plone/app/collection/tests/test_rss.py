# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, setRoles, login

from plone.app.collection.interfaces import ICollection
from plone.app.collection.collection import Collection

from lxml import etree

from .base import CollectionTestCase

query = [{
    u'i': u'portal_type', 
    u'o': u'plone.app.querystring.operation.selection.is', 
    u'v': [u'Document']
}]


class RSSViewTest(CollectionTestCase):

    # def setUp(self):
    #     self.portal = self.layer['portal']
    #     self.request = self.layer['request']
    #     setRoles(self.portal, TEST_USER_ID, ['Manager'])
    #     login(self.portal, TEST_USER_NAME)
    #     self.portal.invokeFactory('Folder', 'test-folder')
    #     self.folder = self.portal['test-folder']
    #     self.folder.invokeFactory('Collection', 
    #                               'collection1')
    #     self.collection = aq_inner(self.folder['collection1'])
    #     self.request.set('URL', self.collection.absolute_url())
    #     self.request.set('ACTUAL_URL', self.collection.absolute_url())

    def assertIsValidRSS(self, rss):
        # XXX: We might want to validate against a DTD or RelaxNG schema here.
        #schema = etree.XMLSchema(schema_root)
        #parser = etree.XMLParser(dtd_validation=True,schema=schema)
        if isinstance(rss, unicode):
            rss = rss.encode("utf-8")
        parser = etree.XMLParser()
        return etree.fromstring(rss, parser)

    def test_view(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        view = collection.restrictedTraverse('@@RSS')
        self.assertTrue(view())
        self.assertEquals(view.request.response.status, 200)
    
    def test_view_is_valid(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        view = collection.restrictedTraverse('@@RSS')
        self.assertIsValidRSS(view())

    def test_rss_feed_includes_collection_results(self):
        portal = self.layer['portal']
        workflow = portal.portal_workflow

        login(portal, 'admin')
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        collection.setQuery(query)

        # Let's add some documents to a folder
        folder = portal['folder_1']
        folder.invokeFactory("Document",
                             "doc1",
                             title="Doc 1")
        workflow.doActionFor(folder.doc1, "publish")
        folder.invokeFactory("Document",
                             "doc2",
                             title="Doc 2")
        workflow.doActionFor(folder.doc2, "publish")
        folder.invokeFactory("Document",
                             "doc3",
                             title="Doc 3")
        workflow.doActionFor(folder.doc3, "publish")
        folder.invokeFactory("Document",
                             "doc4",
                             title="Doc 4")
        workflow.doActionFor(folder.doc4, "publish")

        view = collection.restrictedTraverse('@@RSS')
        contents = view()

        self.assertTrue('Doc 1' in contents)
        self.assertTrue('Doc 2' in contents)
        self.assertTrue('Doc 3' in contents)
        self.assertTrue('Doc 4' in contents)
