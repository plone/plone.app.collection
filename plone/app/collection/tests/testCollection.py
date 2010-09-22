import unittest2 as unittest
from plone.app.collection.tests.base import PACOLLECTION_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser


class TestCollection(unittest.TestCase):

    layer = PACOLLECTION_FUNCTIONAL_TESTING

    def test_viewingCollection(self):
        query = [{
            'i': 'Title',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Collection Test Page',
        }]
        collection = self.layer['portal'].collection
        collection.setQuery(query)
        self.assertEqual(collection.getQuery()[0].Title(),
                         "Collection Test Page")
        browser = Browser(self.layer['app'])
        browser.open(collection.absolute_url())
        self.failUnless("Collection Test Page" in browser.contents)
