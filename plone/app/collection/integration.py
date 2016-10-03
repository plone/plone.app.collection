# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable \
    as IPloneFactoryNonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable \
    as IQuickInstallerNonInstallable
from zope.interface import implementer


@implementer(IQuickInstallerNonInstallable, IPloneFactoryNonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """
        Prevents profiles dependencies from showing up in the profile list
        when creating a Plone site.
        """
        return [u'plone.app.querystring:default',
                ]

    def getNonInstallableProducts(self):
        """
        Prevents our dependencies from showing up in the quick
        installer's list of installable products.
        """
        return [
            'plone.app.querystring',
            ]
