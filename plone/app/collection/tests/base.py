import unittest2 as unittest
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.testing import z2
from zope.configuration import xmlconfig


class PACollection(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        xmlconfig.file('configure.zcml', Products.ATContentTypes,
                       context=configurationContext)
        z2.installProduct(app, 'Products.ATContentTypes')
        import plone.app.collection
        xmlconfig.file('configure.zcml', plone.app.collection,
                       context=configurationContext)
        z2.installProduct(app, 'plone.app.collection')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'Products.ATContentTypes:default')
        applyProfile(portal, 'plone.app.collection:default')
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        setRoles(portal, 'admin', ['Manager'])
        login(portal, 'admin')
        workflow = portal.portal_workflow
        workflow.setDefaultChain('simple_publication_workflow')

        # add a page, so we can test with it
        portal.invokeFactory("Document",
                             "collectiontestpage",
                             title="Collection Test Page")
        workflow.doActionFor(portal.collectiontestpage, "publish")

        # add 6 folders, so we can test with them
        for i in range(6):
            portal.invokeFactory('Folder', 'folder_%s' % i)

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.ATContentTypes')


PACOLLECTION_FIXTURE = PACollection()

PACOLLECTION_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(PACOLLECTION_FIXTURE, ),
                      name="PACollection:Functional")


class CollectionTestCase(unittest.TestCase):

    layer = PACOLLECTION_FUNCTIONAL_TESTING


class CollectionPortletTestCase(unittest.TestCase):

    layer = PACOLLECTION_FUNCTIONAL_TESTING
