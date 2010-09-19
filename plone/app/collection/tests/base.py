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


class RealGSProfile(tcl_ptc.PTCLayer):
    """A PloneTestCase layer that runs the plone.app.collection GenericSetup
       profile.
    """

    def afterSetUp(self):
        self.addProfile('plone.app.collection:default')


class CollectionInstalled(tcl_ptc.BasePTCLayer):
    """A PloneTestCase layer that loads the ZCML for plone.app.collection and
       installs the package into zope.
    """

    def afterSetUp(self):
        import plone.app.collection
        self.loadZCML('configure.zcml', package=plone.app.collection)
        ztc.installPackage('plone.app.collection')

# The layers available to test authors

UninstalledLayer = tcl_ptc.BasePTCLayer([common.common_layer, ])
InstalledLayer = CollectionInstalled([UninstalledLayer, ])
FullProfilelayer = RealGSProfile([InstalledLayer, ])

# Convenient base classes for PloneTestCase


class CollectionTestCase(ptc.PloneTestCase):
    layer = FullProfilelayer


class CollectionFunctionalTestCase(ptc.FunctionalTestCase, CollectionTestCase):
    pass
