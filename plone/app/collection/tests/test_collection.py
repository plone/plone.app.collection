from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import login
from plone.app.testing import logout
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.testing.z2 import Browser
from transaction import commit
from zope.component import getUtility, getMultiAdapter
from Products.CMFCore.utils import getToolByName

from plone.app.collection.portlets import collectionportlet
from .base import CollectionTestCase, CollectionPortletTestCase
from .base import PACOLLECTION_FUNCTIONAL_TESTING

import time

# default test query
query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class TestCollection(CollectionTestCase):

    def test_addCollection(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        self.assertEqual(collection.Title(), "New Collection")

    def test_searchResults(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        collection.setQuery(query)
        self.assertEqual(collection.getQuery()[0].Title(),
                         "Collection Test Page")

    def test_listMetaDataFields(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        metadatafields = collection.listMetaDataFields()
        self.assertTrue(len(metadatafields) > 0)

    def test_viewingCollection(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        # set the query and publish the collection
        collection.setQuery(query)
        workflow = portal.portal_workflow
        workflow.doActionFor(collection, "publish")
        commit()
        logout()
        # open a browser to see if our page is in the results
        browser = Browser(self.layer['app'])
        browser.open(collection.absolute_url())
        self.assertTrue("Collection Test Page" in browser.contents)

    def test_getFoldersAndImages(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")

        # add example folder and a subfolder to it, both with same id
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = portal['folder1']

        folder.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        subfolder = folder['folder1']
        # add example image into folder and its subfolder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")

        subfolder.invokeFactory("Image",
                                "another_image",
                                title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Folder',
        }]
        collection = portal['collection']
        collection.setQuery(query)
        imagecount = collection.getFoldersAndImages()['total_number_of_images']
        self.assertTrue(imagecount == 2)

    def test_limit(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']

        # add two folders as example content
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")

        portal.invokeFactory("Folder",
                             "folder2",
                             title="Folder2")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Folder',
        }]

        collection.setQuery(query)
        collection.setLimit(1)
        results = collection.results(batch=False)
        # fail test if there is more than one result
        self.assertTrue(len(results) == 1)

    def test_selectedViewFields(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        # check if there are selectedViewFields
        self.assertTrue(len(collection.selectedViewFields()) > 0)

    def test_syndication_enabled_by_default(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        syn = getToolByName(portal, 'portal_syndication')
        self.assertTrue(syn.isSyndicationAllowed(collection))

    def test_sorting_1(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        }]
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection",
                             query=query,
                             sort_on='created',
                             sort_reversed=True,
                             )

        # News Item 1
        portal.invokeFactory(id='newsitem1',
                             type_name='News Item')
        time.sleep(2)
        # News Item 1
        portal.invokeFactory(id='newsitem2',
                             type_name='News Item')
        time.sleep(2)
        # News Item 1
        portal.invokeFactory(id='newsitem3',
                             type_name='News Item')

        collection = portal['collection']
        results = collection.results(batch=False)
        ritem0 = results[0]
        ritem1 = results[1]
        ritem2 = results[2]

        self.assertTrue(ritem0.CreationDate() > ritem1.CreationDate())
        self.assertTrue(ritem1.CreationDate() > ritem2.CreationDate())

