import unittest

from plone.app.collection import queryparser
from base import UnittestWithRegistryLayer

from plone.app.collection.queryparser import Row


class MockObject(object):
    def __init__(self, uid, path):
        self.uid = uid
        self.path = path.split("/")

    def getPhysicalPath(self):
        return self.path

    def absolute_url(self):
        return self.path


class MockCatalog(object):
    def lookupObject(self, uid):
        return MockObject(uid='00000000000000001', path="/site/foo")


class MockSite(object):
    def __init__(self):
        self.reference_catalog = MockCatalog()


class MockQuery(object):
    def __init__(self, formquerydata):
        self.formquerydata = formquerydata

    def __iter__(self):
        for x in self.formquerydata:
            yield x


class TestQueryParser(unittest.TestCase):

    layer = UnittestWithRegistryLayer

    def setUp(self):
        super(TestQueryParser, self).setUp()

        self.parser = queryparser.QueryParser(None, None)

        reg = self.layer.registry
        # As this isn't a real registry but a dict we can just set things
        # easily.
        #
        # This seems like the best comprimise between keeping this as a simple
        # unittest and having the API for the form parser be sane by trusting
        # the registry to provide a name->function mapping.
        reg['plone.app.collection.operation.string.is.operation'] = 'plone.app.collection.queryparser:_equal'
        reg['plone.app.collection.operation.string.path.operation'] = 'plone.app.collection.queryparser:_path'

    def test_exact_title(self):
        data = {
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Welcome to Plone',
        }
        query = MockQuery([data, ])
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'Title': {'query': 'Welcome to Plone'}})

    def test_path_explicit(self):
        data = {
            'i': 'path',
            'o': 'plone.app.collection.operation.string.path',
            'v': '/site/foo',
        }
        query = MockQuery([data, ])
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': {'query': '/site/foo'}})

    def test_path_computed(self):
        data = {
            'i': 'path',
            'o': 'plone.app.collection.operation.string.path',
            'v': '00000000000000001',
        }
        query = MockQuery([data, ])

        self.parser.context = MockSite()

        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': {'query': '/site/foo'}})

    # Test the actual query generating
    # XXX: This needs to go in a different test case
    def test__between(self):
        data = Row(index='modified',
                  operator='_between',
                  values=['2009/08/12', '2009/08/14'])
        parsed = queryparser._between(None, data)
        expected = {'modified': {'query': ['2009/08/12', '2009/08/14'],
                    'range': 'minmax'}}
        self.assertEqual(parsed, expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryParser))
    return suite
