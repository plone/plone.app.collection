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

from plone.app.collection.portlets import collectionportlet
from .base import CollectionTestCase, CollectionPortletTestCase
from .base import PACOLLECTION_FUNCTIONAL_TESTING

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

        # add example folder
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = portal['folder1']

        # add example image into the folder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Folder',
        }]
        collection = portal['collection']
        collection.setQuery(query)
        imagecount = collection.getFoldersAndImages()['total_number_of_images']
        self.assertTrue(imagecount == 1)

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


class TestCollectionPortlet(CollectionPortletTestCase):

    layer = PACOLLECTION_FUNCTIONAL_TESTING

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType,
                             name='plone.app.collection.portlets.Collection')
        self.assertEqual(portlet.addview,
                         'plone.app.collection.portlets.Collection')

    def testInterfaces(self):
        portlet = collectionportlet.Assignment(header=u"title")
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType,
                             name='plone.app.collection.portlets.Collection')
        portal = self.layer['portal']
        login(portal, 'admin')
        mapping = portal.restrictedTraverse('++contextportlets++plone.leftcolumn')

        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'header': u"test title"})
        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                   collectionportlet.Assignment))

    def testInvokeEditView(self):
        portal = self.layer['portal']
        mapping = PortletAssignmentMapping()
        request = portal.REQUEST
        mapping['foo'] = collectionportlet.Assignment(header=u"title")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, collectionportlet.EditForm))

    def testRenderer(self):
        portal = self.layer['portal']
        context = portal
        request = portal.REQUEST
        view = portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=context)
        assignment = collectionportlet.Assignment(header=u"title")
        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, collectionportlet.Renderer))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        portal = self.layer['portal']
        context = context or portal
        request = request or portal.REQUEST
        view = view or portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=context)
        assignment = assignment
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testPortlet(self):
        """We test if the basic functionality of the portlet is working and if
           the portlet is returning the same results as the collection"""
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']

        # query for folders
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Folder',
        }]

        # set the query
        collection.setQuery(query)
        collection_num_items = len(collection.results())
        # fail if there are less then 6 results
        self.assertTrue(collection_num_items >= 6)

        # we need to commit the changes, otherwise the collection is not updated
        commit()

        mapping = PortletAssignmentMapping()
        mapping['example'] = collectionportlet.Assignment(header=u"title",
                                                          target_collection='/collection',
                                                          limit=10)
        collectionrenderer = self.renderer(context=None,
                                           request=None,
                                           view=None,
                                           manager=None,
                                           assignment=mapping['example'])

        # we want the portlet to return the same number of results as the collection
        self.assertEqual(collection_num_items, len(collectionrenderer.results()))

        # let's see if the portlet is available as well
        self.assertEqual(collectionrenderer.available, True)

        # set the target_collection to an unicode string, this should work as well
        collectionrenderer.data.target_collection = u"/collection"
        self.assertEqual(collection_num_items, len(collectionrenderer.results()))

        # We test if the portlet is returning the collection url correct
        self.assertEqual(collectionrenderer.collection_url(),
                         "%s/collection" % portal.absolute_url())

        # set the target_collection to an empty value, so we should get an empty result
        collectionrenderer.data.target_collection = ''
        self.assertEqual(len(collectionrenderer.results()), 0)

        # set the target_collection to /, so we should get an empty result
        collectionrenderer.data.target_collection = '/'
        self.assertEqual(len(collectionrenderer.results()), 0)
