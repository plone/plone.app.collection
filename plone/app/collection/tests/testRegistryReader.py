import unittest

from plone.app.collection.tests.base import CollectionRegistryReaderCase
import plone.app.collection.tests.registry_testdata as td
from plone.app.collection.interfaces import ICollectionRegistryReader

class TestRegistryReader(CollectionRegistryReaderCase):
        
    def test_parse_registry(self):
        """tests if the parsed registry data is correct"""
        registry = self.createRegistry(td.minimal_correct_xml)
        reader = ICollectionRegistryReader(registry)
        result = reader.parseRegistry()
        self.assertEqual(result, td.parsed_correct)

    def test_map_operations_clean(self):
        """tests if mapOperations is getting all operators correctly"""
        registry = self.createRegistry(td.minimal_correct_xml)
        reader = ICollectionRegistryReader(registry)
        result = reader.parseRegistry()
        result = reader.mapOperations(result)
        operations = result.get('plone.app.collection.field.created.operations')
        operators = result.get('plone.app.collection.field.created.operators')
        for operation in operations:
            assert operation in operators

    def test_map_operations_missing(self):
        """tests if nonexisting referenced operations are properly skipped"""
        registry = self.createRegistry(td.minimal_missing_operator_xml)
        reader = ICollectionRegistryReader(registry)
        result = reader.parseRegistry()
        result = reader.mapOperations(result)
        operators = result.get('plone.app.collection.field.created.operators').keys()
        assert 'plone.app.collection.operation.date.lessThan' in operators
        assert 'plone.app.collection.operation.date.largerThan' not in operators
        
        
    def test_sortable_indexes(self):
        registry = self.createRegistry(td.minimal_missing_operator_xml)
        reader = ICollectionRegistryReader(registry)
        result = reader.parseRegistry()
        result = reader.mapOperations(result)
        result = reader.mapSortableIndexes(result)
        sortables = result.get('plone.app.collection.field')

        # there should be at least one sortable index
        assert len(sortables)
        
        # confirm that every sortable really is sortable
        for field in sortables.values():
            assert not field['sortable']

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegistryReader))
    return suite
