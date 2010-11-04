import unittest2 as unittest
from plone.app.collection.tests.base import PACOLLECTION_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
from plone.app.testing import login
from plone.app.testing import logout
from transaction import commit
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.app.collection.portlets import collectionportlet
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from Products.CMFCore.utils import getToolByName


# default test query
query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class TestCollection(unittest.TestCase):

    layer = PACOLLECTION_FUNCTIONAL_TESTING

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
        self.failUnless(len(metadatafields) > 0)

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
        self.failUnless("Collection Test Page" in browser.contents)

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
        self.failUnless(imagecount == 1)

    def test_limitNumber(self):
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
        collection.setLimitNumber(True)
        collection.setItemCount(1)
        results = collection.results()
        # fail test if there is more than one result
        self.failUnless(len(results) == 1)

    def test_selectedViewFields(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        # check if there are selectedViewFields
        self.failUnless(len(collection.selectedViewFields()) > 0)


class TestCollectionPortlet(PortletsTestCase):
    """Test the collection portlet"""

    layer = PACOLLECTION_FUNCTIONAL_TESTING

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType,
                             name='plone.app.collection.portlets.Collection')
        self.assertEquals(portlet.addview,
                          'plone.app.collection.portlets.Collection')

    def testInterfaces(self):
        portlet = collectionportlet.Assignment(header=u"title")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType,
                             name='plone.app.collection.portlets.Collection')
        portal = self.layer['portal']
        login(portal, 'admin')
        mapping = portal.restrictedTraverse('++contextportlets++plone.leftcolumn')

        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'header': u"test title"})
        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   collectionportlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST
        mapping['foo'] = collectionportlet.Assignment(header=u"title")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, collectionportlet.EditForm))

    def testRenderer(self):
        context = self.portal
        request = self.portal.REQUEST
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = collectionportlet.Assignment(header=u"title")
        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, collectionportlet.Renderer))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testPortlet(self):
        """We test if the basic functionality of the portlet is working and if
           the portlet is returning the same results as the collection"""
        portal = self.layer['portal']
        login(portal, 'admin')
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
        self.failUnless(collection_num_items >= 6)

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
        self.assertEquals(collection_num_items, len(collectionrenderer.results()))

        # let's see if the portlet is available as well
        self.assertEquals(collectionrenderer.available, True)

        # set the target_collection to an unicode string, this should work as well
        collectionrenderer.data.target_collection = u"/collection"
        self.assertEquals(collection_num_items, len(collectionrenderer.results()))

        # We test if the portlet is returning the collection url correct
        self.assertEquals(collectionrenderer.collection_url(),
                          "%s/collection" % self.portal.absolute_url())

        # set the target_collection to an empty value, so we should get an empty result
        collectionrenderer.data.target_collection = ''
        self.assertEquals(len(collectionrenderer.results()), 0)

        # set the target_collection to /, so we should get an empty result
        collectionrenderer.data.target_collection = '/'
        self.assertEquals(len(collectionrenderer.results()), 0)
