# -*- coding: utf-8 -*-
from Products.Archetypes.Marshall import parseRFC822
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login
from plone.app.testing import logout
from plone.testing.z2 import Browser
from transaction import commit
from zope.event import notify

from .base import CollectionTestCase

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

    def test_customQuery(self):
        portal = self.layer['portal']
        login(portal, 'admin')
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

    def test_collection_templates(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        data = getData('image.png')
        # add an image that will be listed by the collection
        portal.invokeFactory("Image",
                             "image",
                             title="Image example",
                             image=data)
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        # Search for images
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        # set the query and publish the collection
        collection.setQuery(query)
        workflow = portal.portal_workflow
        workflow.doActionFor(collection, "publish")
        commit()
        logout()
        # open a browser to see if our image is in the results
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.open(collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open summary_view template
        browser.open('%s/summary_view' % collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open folder_summary_view template
        browser.open('%s/folder_summary_view' % collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)
        # open thumbnail_view template
        browser.open('%s/thumbnail_view' % collection.absolute_url())
        self.assertTrue("Image example" in browser.contents)

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
        # The current implementation for getFoldersAndImages will return
        # another_image under subfolder and also under folder
        self.assertTrue(imagecount == 3)

    def test_getFoldersAndImages_returning_images(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")

        # add example folder
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = portal['folder1']

        # add example image into this folder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")

        # add another image into the portal root
        portal.invokeFactory("Image",
                             "image",
                             title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
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

    def test_batch(self):
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
        collection.setLimit(2)
        results = collection.results(batch=False)
        self.assertTrue(results.actual_result_count == 2)
        results = collection.results(batch=True, b_size=1)
        self.assertTrue(results.length == 1)
        results = collection.results(batch=True, b_size=3)
        self.assertTrue(results.length == 2)

        collection.setB_size(1)
        results = collection.results()
        self.assertTrue(results.length == 1)

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
        notify(ObjectInitializedEvent(collection))
        syn = getToolByName(portal, 'portal_syndication')
        self.assertTrue(syn.isSyndicationAllowed(collection))


class TestMarshalling(CollectionTestCase):

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
    
