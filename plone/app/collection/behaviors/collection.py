# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from plone.app.contentlisting.interfaces import IContentListing

from plone.app.querystring.querybuilder import QueryBuilder

from plone.dexterity.interfaces import IDexterityContent

from plone.dexterity.content import Item

from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.supermodel import model


from zope.interface import alsoProvides

from plone.app.collection import MessageFactory as _
from plone.app.collection.interfaces import ICollectionBehavior


class CollectionBehavior(object):
    implements(ICollectionBehavior)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    #security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of all metadata fields from portal_catalog.
        """
        return []
        #tool = getToolByName(self, ATCT_TOOLNAME)
        #return tool.getMetadataDisplay(exclude)

    def results(self, batch=True, b_start=0, b_size=None):
        querybuilder = QueryBuilder(self.context, self.request)
        sort_order = 'reverse' if getattr(self, 'sort_reversed', False) else 'ascending'
        if not b_size:
            b_size = getattr(self, 'item_count', None)
        return querybuilder(
            query=getattr(self, 'query', {}),
            batch=batch,
            b_start=b_start, 
            b_size=b_size,
            sort_on=getattr(self, 'sort_on', None), 
            sort_order=sort_order,
            limit=getattr(self, 'limit', None),
        )

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        return []
        #_mapping = {}
        #for field in self.listMetaDataFields().items():
        #    _mapping[field[0]] = field
        #return [_mapping[field] for field in self.customViewFields]

    def getFoldersAndImages(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = self.results(batch=False)

        _mapping = {'results': results, 'images': {}}
        portal_atct = getToolByName(self.context, 'portal_atct')
        image_types = getattr(portal_atct, 'image_types', [])

        for item in results:
            item_path = item.getPath()
            if item.isPrincipiaFolderish:
                query = {
                    'portal_type': image_types,
                    'path': item_path,
                }
                _mapping['images'][item_path] = IContentListing(catalog(query))
            elif item.portal_type in image_types:
                _mapping['images'][item_path] = [item, ]

        _mapping['total_number_of_images'] = sum(map(len,
                                                _mapping['images'].values()))
        return _mapping
