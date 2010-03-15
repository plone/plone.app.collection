import unittest

from plone.app.collection.tests.base import CollectionTestCase

class TestOperationDefinitions(CollectionTestCase):
        
    def test_string_equality(self):
        registry = self.portal.portal_registry
        prefix = "plone.app.collection.operation.string.is"
        
        assert prefix+'.Title' in registry
        
        self.assertEqual(prefix+".Title", "equals")
        self.assertEqual(prefix+".Description", 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(prefix+".operation", 'is')
                
    def test_string_inequality(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.operation.string.is_not'
        assert prefix+".Title" in registry
        
        self.assertEqual(prefix+".Title", "does not equal")
        self.assertEqual(prefix+".Description", 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(prefix+".operation", 'is_not')
    
    def test_date_lessthan(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.operation.date.lessthan'

        assert prefix+".Title" in registry
        
        self.assertEqual(prefix+".Title", "before")
        self.assertEqual(prefix+".Description",
                         'please use YYYY/MM/DD.')
        self.assertEqual(prefix+".operation", 'less_than')

class TestFieldDefinitions(CollectionTestCase):
    
    def test_getId(self):
        registry = self.portal.portal_registry
        prefix = 'plone.app.collection.field.getId'
        assert prefix+".Title" in registry
        
        operations = prefix + ".operations"
        assert len(operations) == 2
        
        equal = 'plone.app.collection.operation.string.is'
        inequal = 'plone.app.collection.operation.string.is_not'
        assert equal in operations
        assert inequal in operations

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOperationDefinitions))
    suite.addTest(unittest.makeSuite(TestFieldDefinitions))
    return suite
