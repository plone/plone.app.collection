from zope.component import getUtility
from Products.Archetypes.Marshall import parseRFC822
from Products.CMFCore.utils import getToolByName
from plone.app.collection.testing import PLONEAPPCOLLECTION_FUNCTIONAL_TESTING
from plone.app.collection.testing import PLONEAPPCOLLECTION_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from transaction import commit
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

    layer = PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.portal.invokeFactory('Collection', 'col')
        self.collection = self.portal['col']

    def _set_up_collection(self):
        self.portal.invokeFactory(
            'Document',
            'doc1',
            title='Collection Test Page'
        )
        self.collection.setQuery(query)

    def test_addCollection(self):
        self.portal.invokeFactory("Collection",
                                  "col1",
                                  title="New Collection")
        self.assertEqual(self.portal.col1.Title(), "New Collection")

    def test_searchResults(self):
        self.portal.invokeFactory('Document',
                                  'doc1',
                                  title='Collection Test Page')
        self.collection.setQuery(query)
        self.assertEqual(
            self.collection.getQuery()[0].Title(),
            "Collection Test Page")

    def test_customQuery(self):
        portal = self.layer['portal']
        login(portal, 'admin')

        # add test content
        portal.invokeFactory('Document',
                             'collectiontestpage',
                             title='Collection Test Page')
        portal.invokeFactory('Folder', 'folder_0', title="Folder 0")

        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']

        testquery = [{
            'i': 'id',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'collectiontestpage',
        }]

        collection.setQuery(testquery)

        # Test unmodified query
        self.assertEqual(len(collection.results()), 1)

        # Test with custom query overwriting original query
        custom_query = {'id': {'query': 'folder_0'}}
        results = collection.results(custom_query=custom_query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 'folder_0')

        # Test with custom query overwriting original query and adding another
        # search term, which cannot be found
        custom_query = {'id': {'query': 'folder_0'}, 'Title': {'query': 'foo'}}
        results = collection.results(custom_query=custom_query)
        self.assertEqual(len(results), 0)

    def test_listMetaDataFields(self):
        metadatafields = self.collection.listMetaDataFields()
        self.assertTrue(len(metadatafields) > 0)

    def test_viewingCollection(self):
        self.portal.invokeFactory(
            'Document',
            'doc1',
            title='Collection Test Page')
        # set the query and publish the collection
        self.collection.setQuery(query)
        commit()
        logout()
        # open a browser to see if our page is in the results
        browser = Browser(self.layer['app'])
        browser.open(self.collection.absolute_url())
        self.assertTrue("Collection Test Page" in browser.contents)

    def test_show_about_logged_in(self):
        """Test the case where we show about information if a user is logged in
        even though show about is set to False
        """
        registry = getUtility(IRegistry)
        registry['plone.allow_anon_views_about'] = False

        self._set_up_collection()

        # check if author information is shown
        result = self.collection.restrictedTraverse('standard_view')()
        self.assertTrue("author" in result)
        self.assertTrue("test-user" in result)

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
        self.assertEqual(imagecount, 2)

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


class TestMarshalling(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_INTEGRATION_TESTING

    def test_simple_query_included_in_marshall_results(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        }]
        portal.invokeFactory("Collection",
                             "collection",
                             query=query,
                             title="New Collection")
        collection = portal['collection']
        rfc822 = collection.manage_FTPget()
        data = parseRFC822(rfc822)
        self.assertIn('query0_i', data[0])
        self.assertIn('query0_o', data[0])
        self.assertIn('query0_v', data[0])

        self.assertEqual(data[0]['query0_i'], query[0]['i'])
        self.assertEqual(data[0]['query0_o'], query[0]['o'])
        self.assertEqual(data[0]['query0_v'], query[0]['v'])

    def test_multiple_query_items_included_in_marshall_results(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        },{ 'i': 'Title',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Test News Item',
        }]

        portal.invokeFactory("Collection",
                             "collection",
                             query=query,
                             title="New Collection")
        collection = portal['collection']
        rfc822 = collection.manage_FTPget()
        data = parseRFC822(rfc822)

        self.assertIn('query0_i', data[0])
        self.assertIn('query0_o', data[0])
        self.assertIn('query0_v', data[0])
        self.assertIn('query1_i', data[0])
        self.assertIn('query1_o', data[0])
        self.assertIn('query1_v', data[0])

        self.assertEqual(data[0]['query0_i'], query[0]['i'])
        self.assertEqual(data[0]['query0_o'], query[0]['o'])
        self.assertEqual(data[0]['query0_v'], query[0]['v'])
        self.assertEqual(data[0]['query1_i'], query[1]['i'])
        self.assertEqual(data[0]['query1_o'], query[1]['o'])
        self.assertEqual(data[0]['query1_v'], query[1]['v'])

    def test_query_gets_set_on_PUT(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        }]

        expected_query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'LOREM IPSUM DOLOR',
        }]

        portal.invokeFactory("Collection",
                             "collection",
                             query=query,
                             title="New Collection")
        collection = portal['collection']
        rfc822 = collection.manage_FTPget()
        # Modify the response to put in a sentinal, to check it's been updated
        rfc822 = rfc822.replace(query[0]['v'], expected_query[0]['v'])

        portal.REQUEST.set("BODY", rfc822)
        collection.PUT(portal.REQUEST, None)
        self.assertEqual(collection.query, expected_query)
