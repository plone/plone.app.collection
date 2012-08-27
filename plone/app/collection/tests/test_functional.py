# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

from plone.app.collection.testing import \
    PLONEAPPCOLLECTION_SELENIUM_TESTING

import gocept.selenium.plonetesting
import  gocept.selenium.plonetesting.testing_plone

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',

}]


class PloneAppCollectionFunctionalTest(gocept.selenium.plonetesting.TestCase):

    layer = PLONEAPPCOLLECTION_SELENIUM_TESTING

    def setUp(self):
        self.sel = self.layer['selenium']
        self.createContent()
        self.login()

    def createContent(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Document', id='doc1', title="Document 1")
        self.portal.invokeFactory('Folder', id='folder1', title="Folder 1")

    def login(self):
        self.sel.open('/plone')
        self.sel.click('link=Log in')
        self.sel.waitForElementPresent('name=__ac_name')
        self.sel.type('name=__ac_name', SITE_OWNER_NAME)
        self.sel.type('name=__ac_password', SITE_OWNER_PASSWORD)
        self.sel.click('name=submit')
        self.sel.waitForPageToLoad()
        self.sel.assertTextPresent(SITE_OWNER_NAME)

    def test_add_collection(self):
        self.sel.open('/plone')
        self.sel.open('/plone/++add++Collection')
        self.sel.waitForElementPresent('name=form.widgets.IBasic.title')
        self.sel.type("name=form.widgets.IBasic.title", 'My Collection')
        self.sel.type(
            'name=form.widgets.IBasic.description',
            'This is a collection.')
        self.sel.type("name=addindex", "portal_type")
        self.sel.click("name=form.widgets.query.v:records:list")
        self.sel.click("name=form.buttons.save")
        self.sel.waitForPageToLoad()
        self.sel.assertTextPresent("My Collection")
        self.sel.assertTextPresent("This is a collection.")
        self.sel.assertTextPresent("Document 1")
        self.sel.assertTextNotPresent("Folder 1")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
