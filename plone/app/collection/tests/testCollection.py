import unittest

from plone.app.collection.tests.base import CollectionTestCase, CollectionFunctionalTestCase
from Products.Five.testbrowser import Browser


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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCollection))
    return suite
