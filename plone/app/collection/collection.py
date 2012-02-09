from AccessControl import ClassSecurityInfo
from archetypes.querywidget.field import QueryField
from archetypes.querywidget.widget import QueryWidget
from plone.app.contentlisting.interfaces import IContentListing
from Products.ATContentTypes.content import document, schemata
from Products.Archetypes import atapi
from Products.Archetypes.atapi import (BooleanField,
                                       BooleanWidget,
                                       IntegerField,
                                       LinesField,
                                       IntegerWidget,
                                       InAndOutWidget,
                                       StringField,
                                       StringWidget)
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from plone.app.collection import PloneMessageFactory as _
from plone.app.collection.config import ATCT_TOOLNAME, PROJECTNAME
from plone.app.collection.interfaces import ICollection


CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((

    QueryField(
        name='query',
        widget=QueryWidget(
            label=_(u"Search terms"),
            description=_(u"Define the search terms for the items you want to "
                          u"list by choosing what to match on. "
                          u"The list of results will be dynamically updated."),
            ),
        validators=('javascriptDisabled', )
        ),

    StringField(
        name='sort_on',
        required=False,
        mode='rw',
        default='sortable_title',
        widget=StringWidget(
            label=_(u'Sort the collection on this index'),
            description='',
            visible=False,
            ),
        ),

    BooleanField(
        name='sort_reversed',
        required=False,
        mode='rw',
        default=False,
        widget=BooleanWidget(
            label=_(u'Sort the results in reversed order'),
            description='',
            visible=False,
            ),
        ),

    IntegerField(
        name='limit',
        required=False,
        mode='rw',
        default=1000,
        widget=IntegerWidget(
            label=_(u'Limit Search Results'),
            description=_(u"Specify the maximum number of items to show.")
            ),
        ),

    LinesField('customViewFields',
        required=False,
        mode='rw',
        default=('Title', 'Creator', 'Type', 'ModificationDate'),
        vocabulary='listMetaDataFields',
        enforceVocabulary=True,
        write_permission=ModifyPortalContent,
        widget=InAndOutWidget(
            label=_(u'Table Columns'),
            description=_(u"Select which fields to display when "
                          u"'Tabular view' is selected in the display menu.")
            ),
        ),
))

CollectionSchema.moveField('query', after='description')
CollectionSchema['presentation'].widget.visible = False
CollectionSchema['tableContents'].widget.visible = False


schemata.finalizeATCTSchema(
    CollectionSchema,
    folderish=False,
    moveDiscussion=False)


class Collection(document.ATDocument):
    """A (new style) Plone Collection"""
    implements(ICollection)

    meta_type = "Collection"
    schema = CollectionSchema

    security = ClassSecurityInfo()

    security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog.
        """
        tool = getToolByName(self, ATCT_TOOLNAME)
        return tool.getMetadataDisplay(exclude)

    def results(self, batch=True, b_start=0, b_size=30):
        """Get results"""
        return self.getQuery(batch=batch, b_start=b_start, b_size=b_size)

    def selectedViewFields(self):
        """Get which metadata field are selected"""
        _mapping = {}
        for field in self.listMetaDataFields().items():
            _mapping[field[0]] = field
        return [_mapping[field] for field in self.customViewFields]

    def getFoldersAndImages(self):
        """Get folders and images"""
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


atapi.registerType(Collection, PROJECTNAME)
