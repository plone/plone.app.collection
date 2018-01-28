# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """
        Prevents profiles dependencies from showing up in the profile list
        when creating a Plone site.
        """
        return [
            'plone.app.collection:uninstall',
            'plone.app.querystring:default',
        ]

    def getNonInstallableProducts(self):
        """
        Prevents our dependencies from showing up in the quick
        installer's list of installable products.
        """
        return [
            'plone.app.querystring',
        ]
