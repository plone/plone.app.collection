# -*- coding: utf-8 -*-
from Acquisition import aq_base

from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from plone.dexterity.content import Item

from plone.app.querystring import queryparser


class Collection(Item):

    #security.declareProtected(View, 'listMetaDataFields')
    #def listMetaDataFields(self, exclude=True):
    #    """Return a list of metadata fields from portal_catalog.
    #    """
    #    tool = getToolByName(self, ATCT_TOOLNAME)
    #    return tool.getMetadataDisplay(exclude)
    
    def results(self, batch=True, b_start=0, b_size=30):
        queryparser.parseFormquery(self, self.query)
        querybuilder = getMultiAdapter((self, self.REQUEST),
                                       name="querybuilderresults")
        return querybuilder(query=self.query,
                            batch=batch, b_start=b_start, b_size=b_size,
                            sort_on=None, sort_order=None, limit=0)

    def selectedViewFields(self):
        return
        _mapping = {}
        for field in self.listMetaDataFields().items():
            _mapping[field[0]] = field
        return [_mapping[field] for field in self.customViewFields]

    def getFoldersAndImages(self):
        return
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
