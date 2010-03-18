import unittest

from plone.registry.interfaces import IRegistry
from plone.registry import Registry
from zope.component import getGlobalSiteManager
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc

from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common
from collective.testcaselayer.layer import Layer as BaseLayer

class CollectionsInstalled(tcl_ptc.BasePTCLayer):
    """Install plone.app.collection"""

    def afterSetUp(self):
        import plone.app.collection
        self.loadZCML('configure.zcml', package=plone.app.collection)
        ztc.installPackage('plone.app.collection')
        
class RealGSProfile(tcl_ptc.PTCLayer):

    def afterSetUp(self):
        self.addProfile('plone.app.collection:default')

class TestGSProfile(tcl_ptc.PTCLayer):
    
    def afterSetUp(self):
        import plone.app.collection.tests
        self.loadZCML('configure.zcml', package=plone.app.collection.tests)
        self.addProfile('plone.app.collection.tests:registry')

class RegistryLayer(BaseLayer):
    
    def setUp(self):
        gsm = getGlobalSiteManager()
        self.registry = Registry()
        gsm.registerUtility(self.registry, IRegistry)
    
    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(provided=IRegistry)

UnittestLayer = BaseLayer([], name="UnittestLayer")
UnittestWithRegistryLayer = RegistryLayer([UnittestLayer, ])
UninstalledLayer = tcl_ptc.BasePTCLayer([common.common_layer, ])
InstalledLayer = CollectionsInstalled([UninstalledLayer, ])
TestProfileLayer = TestGSProfile([InstalledLayer, ])
FullProfilelayer = RealGSProfile([InstalledLayer, ])

class CollectionTestCase(ptc.PloneTestCase):
    layer = FullProfilelayer    
    
class CollectionRegistryReaderCase(unittest.TestCase):
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
    

class CollectionFunctionalTestCase(ptc.FunctionalTestCase):
    layer = FullProfilelayer