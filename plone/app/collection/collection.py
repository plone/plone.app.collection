# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from plone.app.contentlisting.interfaces import IContentListing

from plone.app.querystring.querybuilder import QueryBuilder

from plone.dexterity.content import Container


class Collection(Container):

    #security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of all metadata fields from portal_catalog.
        """
        return []
        #tool = getToolByName(self, ATCT_TOOLNAME)
        #return tool.getMetadataDisplay(exclude)

    def results(self, batch=True, b_start=0, b_size=None):
        querybuilder = QueryBuilder(self, self.REQUEST)
        sort_order = 'reverse' if self.sort_reversed else 'ascending'
        if not b_size:
            b_size = self.item_count
        return querybuilder(query=self.query,
                            batch=batch, b_start=b_start, b_size=b_size,
                            sort_on=self.sort_on, sort_order=sort_order,
                            limit=self.limit)

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
        catalog = getToolByName(self, 'portal_catalog')
        folders = [item for item in self.results(batch=False)
                   if item.portal_type == 'Folder']

        _mapping = {'folders': folders, 'images': {}}

        for folder in folders:
            query = {
                'portal_type': 'Image',
                'path': folder.getPath(),
            }
            _mapping['images'][folder.id] = IContentListing(catalog(query))

        _mapping['total_number_of_images'] = sum(map(len,
                                                _mapping['images'].values()))
        return _mapping
