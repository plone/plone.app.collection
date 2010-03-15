import unittest

from plone.app.collection.tests.base import CollectionTestCase

class TestOperationDefinitions(CollectionTestCase):
        
    def test_string_equality(self):
        registry = self.portal.portal_registry
        assert 'plone.app.collection.operation.string.is' in registry
        config = registry['plone.app.collection.operation.string.is']
        
        self.assertEqual(config.Title, "equals")
        self.assertEqual(config.Description, 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(config.opertation, 'is')
                
    def test_string_inequality(self):
        registry = self.portal.portal_registry
        assert 'plone.app.collection.operation.string.is_not' in registry
        config = registry['plone.app.collection.operation.string.is_not']
        
        self.assertEqual(config.Title, "does not equal")
        self.assertEqual(config.Description, 
                         'Tip: you can use * to autocomplete.')
        self.assertEqual(config.opertation, 'is_not')
    
    def test_date_lessthan(self):
        registry = self.portal.portal_registry
        assert 'plone.app.collection.operation.date.lessthan' in registry
        config = registry['plone.app.collection.operation.date.lessthan']
        
        self.assertEqual(config.Title, "before")
        self.assertEqual(config.Description, 
                         'please use YYYY/MM/DD.')
        self.assertEqual(config.opertation, 'less_than')

class TestFieldDefinitions(CollectionTestCase):
    
    def test_getId(self):
        registry = self.portal.portal_registry
        assert 'plone.app.collection.field.getId' in registry
        config = registry['plone.app.collection.field.getId']
        
        operations = config.operations
        assert len(operations) == 2
        
        equal = registry['plone.app.collection.operation.string.is']
        inequal = registry['plone.app.collection.operation.string.is_not']
        assert equal in operations
        assert inequal in operations

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOperationDefinitions))
    suite.addTest(unittest.makeSuite(TestFieldDefinitions))
    return suite
