import doctest

from zope.configuration import xmlconfig

from plone.testing.z2 import ZSERVER_FIXTURE

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


class PloneAppCollectionLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import plone.app.collection
        xmlconfig.file('configure.zcml', plone.app.collection,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.collection:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            "Folder",
            id="acceptance-test-folder",
            title=u"Test Folder"
        )


PLONEAPPCOLLECTION_FIXTURE = PloneAppCollectionLayer()

PLONEAPPCOLLECTION_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Integration")
PLONEAPPCOLLECTION_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Functional")
PLONEAPPCOLLECTION_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PLONEAPPCOLLECTION_FIXTURE, ZSERVER_FIXTURE),
    name="PloneAppCollectionLayer:Acceptance")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)