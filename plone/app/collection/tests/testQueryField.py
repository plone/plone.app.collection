import unittest

from plone.app.collection.tests.base import CollectionTestCase

class TestQueryField(CollectionTestCase):
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        collection_id = self.portal.invokeFactory("Collection", "NuCollection")
        self.collection = portal[collection_id]
    
    def test_getId(self):
        query = [{
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Welcome to Plone',
        }]
        self.collection.setQuery(query)
        self.assertEqual(query, self.collection.getRawQuery())
        self.assertEqual(len(self.collection.getQuery()))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryField))
    return suite
