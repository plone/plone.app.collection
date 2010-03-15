import unittest

from plone.app.collection.queryparser import QueryParser

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
    
    def setUp(self):
        super(TestQueryParser, self).setUp()
        self.parser = QueryParser(None, None)
            
    def test_exact_title(self):
        query = {'i':'Title', 'o':'is', 'v': 'Welcome to Plone'},
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'Title': 'Welcome to Plone'})
    
    def test_path_explicit(self):
        query = {'i':'path', 'o':'path', 'v': '/site/foo'},
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': '/site/foo'})
    
    def test_path_computed(self):
        query = {'i':'path', 'o':'path', 'v': '00000000000000001'},
        
        self.parsed.context = MockSite()
        
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'path': '/site/foo'})
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryParser))
    return suite
