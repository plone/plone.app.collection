import unittest

from plone.app.collection import queryparser
from plone.registry import field
from plone.registry import Record

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


class TestQueryParserBase(unittest.TestCase):

    layer = UnittestWithRegistryLayer

    def setUp(self):
        super(TestQueryParserBase, self).setUp()

        self.parser = queryparser.QueryParser(None, None)

        self.setFunctionForOperation('plone.app.collection.operation.string.is.operation', 'plone.app.collection.queryparser:_equal')
        self.setFunctionForOperation('plone.app.collection.operation.string.path.operation', 'plone.app.collection.queryparser:_path')

    def setFunctionForOperation(self, operation, function):
        function_field = field.ASCIILine(title=u"Operator")
        function_record = Record(function_field)
        function_record.value = function
        self.layer.registry.records[operation] = function_record

class TestQueryParser(TestQueryParserBase):

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


class TestQueryGenerators(TestQueryParserBase):
    
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
    suite.addTest(unittest.makeSuite(TestQueryGenerators))
    return suite
