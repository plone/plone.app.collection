import unittest

from plone.registry.interfaces import IRegistry
from plone.registry import Registry
from zope.component import getGlobalSiteManager

from plone.app.collection.interfaces import ICollectionRegistryReader
from plone.app.collection.tests.base import InstalledLayer
import plone.app.collection.tests.registry_testdata as td

class TestRegistryReader(unittest.TestCase):
    layer = InstalledLayer

    def getLogger(self, value):
        return 'plone.app.collection'

    def shouldPurge(self):
        return False
    
    def createRegistry(self, xml):
        """Create a registry from a minimal set of fields and operators"""
        from plone.app.registry.exportimport.handler import RegistryImporter
        gsm = getGlobalSiteManager()
        self.registry = Registry()
        gsm.registerUtility(self.registry, IRegistry)
        
        importer = RegistryImporter(self.registry, self)
        importer.importDocument(xml)
        return self.registry
    
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
        """tests if sortable indexes from the registry will be available in
           the parsed registry
        """
        registry = self.createRegistry(td.minimal_correct_xml)
        reader = ICollectionRegistryReader(registry)
        result = reader.parseRegistry()
        result = reader.mapOperations(result)
        result = reader.mapSortableIndexes(result)
        sortables = result['sortable']

        # there should be one sortable index
        assert len(sortables) == 1

        # confirm that every sortable really is sortable
        for field in sortables.values():
            assert field['sortable'] == True


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegistryReader))
    return suite
