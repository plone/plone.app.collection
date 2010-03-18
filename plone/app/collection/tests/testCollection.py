import unittest

from plone.app.collection.tests.base import CollectionTestCase, CollectionFunctionalTestCase
from Products.Five.testbrowser import Browser
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest 


class TestCollection(CollectionFunctionalTestCase):
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        collection_id = self.portal.invokeFactory("Collection", "NewCollection")
        self.collection = self.portal[collection_id]
        self.portal.portal_workflow.doActionFor(self.collection, 'publish')
    
        testpage_id = self.portal.invokeFactory("Document",'collectionstestpage', title="Collectionstestpage")
        self.portal.portal_workflow.doActionFor(self.portal['collectionstestpage'], 'publish')
        
    def test_viewingCollection(self):
        query = [{
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Collectionstestpage',
        }]
        self.collection.setQuery(query)
        self.assertEqual(self.collection.getQuery()[0].Title(), "Collectionstestpage")
        browser = Browser()
        browser.open(self.collection.absolute_url())
        self.failUnless("Collectionstestpage" in browser.contents)

class TestQuerybuilder(CollectionTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        testpage_id = self.portal.invokeFactory("Document",'collectionstestpage', title="Collectionstestpage")
        self.portal.portal_workflow.doActionFor(self.portal['collectionstestpage'], 'publish')
        self.request = TestRequest()      
        self.querybuilder = getMultiAdapter((self.portal, self.request), name='querybuilderresults')
        self.query = [{
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Collectionstestpage',
        }]
        
    def testQueryBuilderQuery(self):
        results = self.querybuilder(query=self.query)
        self.assertEqual(results[0].Title(), "Collectionstestpage")

    def testQueryBuilderNumberOfResults(self):
        self.assertEqual(self.querybuilder.number_of_results(self.query),1)

    def testQueryBuilderHTML(self):        
        self.failUnless('Collectionstestpage' in self.querybuilder.html_results(self.query))




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCollection))
    suite.addTest(unittest.makeSuite(TestQuerybuilder))
    return suite
