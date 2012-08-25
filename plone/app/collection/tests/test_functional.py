# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
import unittest2 as unittest

from plone.app.collection.testing import \
    PLONEAPPCOLLECTION_INTEGRATION_TESTING
from plone.app.collection.testing import \
    PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

import gocept.selenium.plonetesting
import  gocept.selenium.plonetesting.testing_plone

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',

}]


class PloneAppCollectionFunctionalTest(gocept.selenium.plonetesting.TestCase):

    layer = gocept.selenium.plonetesting.testing_plone.selenium_layer

#    layer = gocept.selenium.zope2.Layer(
#        PLONEAPPCOLLECTION_INTEGRATION_TESTING)

    def setUp(self):
        pass

    def test_login(self):
        sel = self.layer['selenium']
        sel.open('/plone')
        sel.click('link=Log in')
        sel.waitForElementPresent('name=__ac_name')
        sel.type('name=__ac_name', SITE_OWNER_NAME)
        sel.type('name=__ac_password', SITE_OWNER_PASSWORD)
        sel.click('name=submit')
        sel.waitForPageToLoad()
        sel.assertTextPresent(SITE_OWNER_NAME)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
