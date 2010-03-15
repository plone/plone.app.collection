from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common

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
        

Installedlayer = Layer([common.common_layer])
UninstalledLayer = tcl_ptc.BasePTCLayer([common.common_layer])

class CollectionTestCase(ptc.PloneTestCase):
    layer = Installedlayer
