from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
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
from plone.app.collection.testing import PLONEAPPCOLLECTION_INTEGRATION_TESTING
import time
import unittest2 as unittest

# default test query
query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


def getData(filename):
    from os.path import dirname, join
    from plone.app.collection import tests
    filename = join(dirname(tests.__file__), filename)
    data = open(filename).read()
    return data


class TestCollection(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        try:
            self.portal.invokeFactory('Collection', 'col')
        except:
            pass
        self.collection = self.portal['col']

    def test_addCollection(self):
        self.portal.invokeFactory("Collection",
                                  "col1",
                                  title="New Collection")
        self.assertEqual(self.portal.col1.Title(), "New Collection")

    def test_searchResults(self):
        self.portal.invokeFactory('Document', 'doc1', title='Collection Test Page')
        self.collection.setQuery(query)
        self.assertEqual(
            self.collection.getQuery()[0].Title(),
            "Collection Test Page")

    def test_listMetaDataFields(self):
        metadatafields = self.collection.listMetaDataFields()
        self.assertTrue(len(metadatafields) > 0)

    def test_viewingCollection(self):
        self.portal.invokeFactory('Document', 'doc1', title='Collection Test Page')
        # set the query and publish the collection
        self.collection.setQuery(query)
        commit()
        logout()
        # open a browser to see if our page is in the results
        browser = Browser(self.layer['app'])
        browser.open(self.collection.absolute_url())
        self.assertTrue("Collection Test Page" in browser.contents)

    def test_collection_templates(self):
        data = getData('image.png')
        # add an image that will be listed by the collection
        self.portal.invokeFactory("Image",
                             "image",
                             title="Image example",
                             image=data)
        # Search for images
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        # set the query and publish the collection
        self.collection.setQuery(query)
        commit()
        logout()
        # open a browser to see if our image is in the results
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.open(self.collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open summary_view template
        browser.open('%s/summary_view' % self.collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open folder_summary_view template
        browser.open('%s/folder_summary_view' % self.collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open thumbnail_view template
        browser.open('%s/thumbnail_view' % self.collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)

    def test_getFoldersAndImages(self):
        collection = self.collection

        # add example folder and a subfolder to it, both with same id
        self.portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = self.portal['folder1']

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
        collection.setQuery(query)
        imagecount = collection.getFoldersAndImages()['total_number_of_images']
        # The current implementation for getFoldersAndImages will return
        # another_image under subfolder and also under folder
        self.assertTrue(imagecount == 3)

    def test_getFoldersAndImages_returning_images(self):
        collection = self.collection
        # add example folder
        self.portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = self.portal['folder1']

        # add example image into this folder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")

        # add another image into the self.portal root
        self.portal.invokeFactory("Image",
                             "image1",
                             title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        collection.setQuery(query)
        imagecount = collection.getFoldersAndImages()['total_number_of_images']
        self.assertEqual(imagecount, 3)

    def test_limit(self):
        collection = self.collection

        # add two folders as example content
        self.portal.invokeFactory(
            "Folder",
            "folder1",
            title="Folder1"
        )

        self.portal.invokeFactory("Folder",
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
        # check if there are selectedViewFields
        self.assertTrue(len(self.collection.selectedViewFields()) > 0)

    def test_syndication_enabled_by_default(self):
        syn = getToolByName(self.portal, 'portal_syndication')
        self.assertTrue(syn.isSyndicationAllowed(self.collection))
