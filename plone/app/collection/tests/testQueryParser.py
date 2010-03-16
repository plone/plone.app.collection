import unittest

from plone.app.collection.queryparser import QueryParser
from base import UnittestWithRegistryLayer

class MockObject(object):
    def __init__(self, uid, path):
        self.uid = uid
        self.path = path.split("/")
    
    def getPhysicalPath(self):
        return self.path
    
class MockCatalog(object):
    def lookupObject(self, uid):
        return MockObject(uid='00000000000000001', path="/site/foo")
    
class MockSite(object):
    def __init__(self):
        self.reference_catalog = MockCatalog()

class TestQueryParser(unittest.TestCase):
    
    layer = UnittestWithRegistryLayer
    
    def setUp(self):
        super(TestQueryParser, self).setUp()
        self.parser = QueryParser(None, None)
        
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
        query = {'i':'Title', 'o':'plone.app.collection.operation.string.is', 'v': 'Welcome to Plone'},
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'Title': 'Welcome to Plone'})
    
    def test_path_explicit(self):
        query = {'i':'path', 'o':'plone.app.collection.operation.string.path', 'v': '/site/foo'},
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': '/site/foo'})
    
    def test_path_computed(self):
        query = {'i':'path', 'o':'plone.app.collection.operation.string.path', 'v': '00000000000000001'},
        
        self.parser.context = MockSite()
        
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': '/site/foo'})
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryParser))
    return suite
