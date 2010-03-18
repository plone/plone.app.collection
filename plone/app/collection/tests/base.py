from plone.registry.interfaces import IRegistry
from plone.registry import Registry
from zope.component import getGlobalSiteManager
from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc

from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common
from collective.testcaselayer.layer import Layer as BaseLayer

# What follows are the class definitions for the test case layers. Don't use 
# these directly, use the instances beneath

class RegistryLayer(BaseLayer): 
    """A unittest layer that provides a new plone.registry. """

    def setUp(self): 
        gsm = getGlobalSiteManager() 
        self.registry = Registry()
        gsm.registerUtility(self.registry, IRegistry)
    
    def tearDown(self): 
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(provided=IRegistry)

class CollectionsInstalled(tcl_ptc.BasePTCLayer):
    """A PloneTestCase layer that loads the ZCML for plone.app.collection and 
       installs the package into zope.
    """

    def afterSetUp(self):
        import plone.app.collection
        self.loadZCML('configure.zcml', package=plone.app.collection)
        ztc.installPackage('plone.app.collection')
        
class RealGSProfile(tcl_ptc.PTCLayer):
    """A PloneTestCase layer that runs the plone.app.collection GenericSetup 
       profile.
    """
    
    def afterSetUp(self):
        self.addProfile('plone.app.collection:default')

class TestGSProfile(tcl_ptc.PTCLayer):
    """A PloneTestCase layer that runs a GenericSetup profile containing test 
       data.
    """

    def afterSetUp(self):
        import plone.app.collection.tests
        self.loadZCML('configure.zcml', package=plone.app.collection.tests)
        self.addProfile('plone.app.collection.tests:registry')

# The layers available to test authors

UnittestLayer = BaseLayer([], name="UnittestLayer")
UnittestWithRegistryLayer = RegistryLayer([UnittestLayer, ])
UninstalledLayer = tcl_ptc.BasePTCLayer([common.common_layer, ])
InstalledLayer = CollectionsInstalled([UninstalledLayer, ])
TestProfileLayer = TestGSProfile([InstalledLayer, ])
FullProfilelayer = RealGSProfile([InstalledLayer, ])

# Convenient base classes for PloneTestCase

class CollectionTestCase(ptc.PloneTestCase):
    layer = FullProfilelayer

class CollectionFunctionalTestCase(ptc.FunctionalTestCase, CollectionTestCase):
    pass