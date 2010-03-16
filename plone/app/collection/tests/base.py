from plone.registry.interfaces import IRegistry
from zope.component import getGlobalSiteManager

from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common
from collective.testcaselayer.layer import Layer as BaseLayer
from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc

class Layer(tcl_ptc.BasePTCLayer):
    """Install plone.app.collection"""

    def afterSetUp(self):
        ztc.installPackage('plone.app.registry')
        ztc.installPackage('plone.app.contentlisting')
        ztc.installPackage('plone.app.collection')

        import plone.app.registry
        import plone.app.contentlisting
        import plone.app.collection

        self.loadZCML('configure.zcml', package=plone.app.registry)
        self.loadZCML('configure.zcml', package=plone.app.contentlisting)
        self.loadZCML('configure.zcml', package=plone.app.collection)
        
        self.addProfile('plone.app.collection:default')

class RegistryLayer(BaseLayer):
    
    def setUp(self):
        gsm = getGlobalSiteManager()
        
        # We don't actually care about having a real registry, just as long as
        # we can find it in the same way and it's dictish
        self.registry = dict()

        gsm.registerUtility(self.registry, IRegistry)

UnittestLayer = BaseLayer([], name="UnittestLayer")
UnittestWithRegistryLayer = RegistryLayer([UnittestLayer])
Installedlayer = Layer([common.common_layer])
UninstalledLayer = tcl_ptc.BasePTCLayer([common.common_layer])

class CollectionTestCase(ptc.PloneTestCase):
    layer = Installedlayer
