# -*- coding: utf-8 -*-
import os
import unittest2 as unittest

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.collection.testing import (
    PLONEAPPCOLLECTION_FUNCTIONAL_TESTING
)

from plone.app.collection.interfaces import IPloneAppCollectionLayer
from zope.interface import alsoProvides

from plone.dexterity.fti import DexterityFTI

from plone.app.testing import TEST_USER_ID, setRoles


class CollectionBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = DexterityFTI('collectiondoc')
        self.portal.portal_types._setObject('collectiondoc', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.behaviors = (
            'plone.app.collection.interfaces.ICollectionBehavior',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppCollectionLayer)
        alsoProvides(self.request, IPloneAppCollectionLayer)
        from plone.app.collection.behaviors.collection import ICollectionBehavior
        alsoProvides(self.request, ICollectionBehavior)
        self.portal.invokeFactory(
            'collectiondoc',
            id='collectiondoc',
            title=u'My Collection Document'
        )
        import transaction
        transaction.commit()
        # Set up browser
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_collection_behaivor_in_edit_form(self):
        self.browser.open(self.portal_url + '/collectiondoc/edit')
        self.assertTrue('Title' in self.browser.contents)
        self.assertTrue('Description' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
