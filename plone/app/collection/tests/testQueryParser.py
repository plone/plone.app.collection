import unittest

from plone.app.collection import queryparser
from plone.registry import field
from plone.registry import Record

from base import UnittestWithRegistryLayer
from plone.app.collection.queryparser import Row

from DateTime import DateTime


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
    def __init__(self, portal_membership=None):
        self.reference_catalog = MockCatalog()
        self.portal_membership = portal_membership


class MockUser(object):
    def __init__(self, username=None):
        self.username = 'Anonymous User'
        if username:
            self.username = username

    def getUserName(self):
        return self.username


class MockPortal_membership(object):
    def __init__(self, user):
        self.user = user

    def getAuthenticatedMember(self):
        return self.user


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
        parsed = self.parser.parseFormquery([data, ])
        self.assertEqual(parsed, {'Title': {'query': 'Welcome to Plone'}})

    def test_path_explicit(self):
        data = {
            'i': 'path',
            'o': 'plone.app.collection.operation.string.path',
            'v': '/site/foo',
        }
        parsed = self.parser.parseFormquery([data, ])
        self.assertEqual(parsed, {'path': {'query': '/site/foo'}})

    def test_path_computed(self):
        data = {
            'i': 'path',
            'o': 'plone.app.collection.operation.string.path',
            'v': '00000000000000001',
        }

        self.parser.context = MockSite()
        parsed = self.parser.parseFormquery([data, ])
        self.assertEqual(parsed, {'path': {'query': '/site/foo'}})


class TestQueryGenerators(TestQueryParserBase):

    def test__between(self):
        data = Row(index='modified',
                  operator='_between',
                  values=['2009/08/12', '2009/08/14'])
        parsed = queryparser._between(MockSite(), data)
        expected = {'modified': {'query': ['2009/08/12', '2009/08/14'],
                    'range': 'minmax'}}
        self.assertEqual(parsed, expected)

    def test__between_reversed_dates(self):
        data = Row(index='modified',
                  operator='_between',
                  values=['2009/08/14', '2009/08/12'])
        parsed = queryparser._between(MockSite(), data)
        expected = {'modified': {'query': ['2009/08/12', '2009/08/14'],
                    'range': 'minmax'}}
        self.assertEqual(parsed, expected)

    def test__largerThan(self):
        data = Row(index='modified',
                  operator='_largerThan',
                  values='2010/03/18')
        parsed = queryparser._largerThan(MockSite(), data)
        expected = {'modified': {'query': '2010/03/18', 'range': 'min'}}
        self.assertEqual(parsed, expected)

    def test__lessThan(self):
        data = Row(index='modified',
                  operator='_lessThan',
                  values='2010/03/18')
        parsed = queryparser._lessThan(MockSite(), data)
        expected = {'modified': {'query': '2010/03/18', 'range': 'max'}}
        self.assertEqual(parsed, expected)

    def test__currentUser(self):

        # Anonymous user
        u = MockUser()
        pm = MockPortal_membership(user=u)
        context = MockSite(portal_membership=pm)
        data = Row(index='Creator',
                  operator='_currentUser',
                  values=None)
        parsed = queryparser._currentUser(context, data)
        expected = {'Creator': {'query': 'Anonymous User'}}
        self.assertEqual(parsed, expected)

        # Logged in user 'admin'
        u = MockUser(username='admin')
        pm = MockPortal_membership(user=u)
        context = MockSite(portal_membership=pm)
        data = Row(index='Creator',
                  operator='_currentUser',
                  values=None)
        parsed = queryparser._currentUser(context, data)
        expected = {'Creator': {'query': 'admin'}}
        self.assertEqual(parsed, expected)

    def test__lessThanRelativeDate(self):
        def test(days):
            now = DateTime()
            mydate = now + days
            mydate = mydate.earliestTime()
            data = Row(index='modified',
                      operator='_lessThanRelativeDate',
                      values=days)
            parsed = queryparser._lessThanRelativeDate(MockSite(), data)
            expected = {'modified': {'query': mydate, 'range': 'max'}}
            self.assertEqual(parsed, expected)

        test(2)
        test(-2)

    def test__moreThanRelativeDate(self):
        def test(days):
            now = DateTime()
            mydate = now + days
            mydate = mydate.latestTime()
            data = Row(index='modified',
                      operator='_moreThanRelativeDate',
                      values=days)
            parsed = queryparser._moreThanRelativeDate(MockSite(), data)
            expected = {'modified': {'query': mydate, 'range': 'min'}}
            self.assertEqual(parsed, expected)

        test(2)
        test(-2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryParser))
    suite.addTest(unittest.makeSuite(TestQueryGenerators))
    return suite
