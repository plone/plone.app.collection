import unittest

from plone.app.collection.tests.base import CollectionTestCase

class TestOperationDefinitions(CollectionTestCase):
        
    def test_string_equality(self):
        registry = self.portal.portal_registry
        prefix = "plone.app.collection.operation.string.is"
        assert prefix+'.title' in registry
        
        self.assertEqual(registry[prefix+".title"], "equals")
        self.assertEqual(registry[prefix+".description"], 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(registry[prefix+".operation"], 'plone.app.collection.queryparser:_equal')
                
    def test_string_inequality(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.operation.string.isNot'
        assert prefix+".title" in registry
        
        self.assertEqual(registry[prefix+".title"], "does not equal")
        self.assertEqual(registry[prefix+".description"], 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(registry[prefix+".operation"], 'plone.app.collection.queryparser:_notEqual')
    
    def test_date_lessthan(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.operation.date.lessThan'

        assert prefix+".title" in registry
        
        self.assertEqual(registry[prefix+".title"], "before")
        self.assertEqual(registry[prefix+".description"],
                         'Please use YYYY/MM/DD.')
        self.assertEqual(registry[prefix+".operation"], 'plone.app.collection.queryparser:_lessThan')

class TestFieldDefinitions(CollectionTestCase):
    
    def test_getId(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.field.getId'
        assert prefix+".title" in registry

        self.assertEqual(registry[prefix+".title"], "Short Name")
        
        operations = registry[prefix + ".operations"]
        assert len(operations) == 2
        
        equal = 'plone.app.collection.operation.string.is'
        inequal = 'plone.app.collection.operation.string.isNot'
        assert equal in operations
        assert inequal in operations

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOperationDefinitions))
    suite.addTest(unittest.makeSuite(TestFieldDefinitions))
    return suite
