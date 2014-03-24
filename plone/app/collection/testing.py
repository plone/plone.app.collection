import doctest

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


class PloneAppCollectionLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'plone.app.collection')
        import plone.app.collection
        xmlconfig.file(
            'configure.zcml',
            plone.app.collection,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.ATContentTypes:default')
        applyProfile(portal, 'plone.app.collection:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        portal.invokeFactory(
            "Folder",
            id="test-folder",
            title=u"Test Folder"
        )

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.ATContentTypes')
        z2.uninstallProduct(app, 'Products.Archetypes')

PLONEAPPCOLLECTION_FIXTURE = PloneAppCollectionLayer()

PLONEAPPCOLLECTION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Integration")
PLONEAPPCOLLECTION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Functional")
PLONEAPPCOLLECTION_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PLONEAPPCOLLECTION_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneAppCollectionLayer:Acceptance")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
