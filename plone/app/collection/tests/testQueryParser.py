import unittest

from plone.app.collection.queryparser import QueryParser

class TestQueryParser(unittest.TestCase):
    
    def setUp(self):
        super(TestQueryParser, self).setUp()
        self.parser = QueryParser(None, None)
            
    def test_exact_title(self):
        query = {'i':'Title', 'o':'is', 'v': 'Welcome to Plone'},
        parsed = self.parser.parseFormquery(query)
        self.assertEqual(parsed, {'Title': 'Welcome to Plone'})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryParser))
    return suite
