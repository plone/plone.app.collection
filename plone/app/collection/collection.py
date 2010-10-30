"""
    Definition of the Collection content type
"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent, View

from Products.Archetypes import atapi
from Products.Archetypes.atapi import (BooleanField,
                                       BooleanWidget,
                                       IntegerField,
                                       LinesField,
                                       IntegerWidget,
                                       InAndOutWidget,
                                       StringField,
                                       StringWidget)
from Products.Archetypes.fieldproperty import ATToolDependentFieldProperty
from Products.ATContentTypes.content import document, schemata

from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME, ATCT_TOOLNAME
from plone.app.collection import PloneMessageFactory as _

from plone.app.contentlisting.interfaces import IContentListing

from archetypes.querywidget.field import QueryField
from archetypes.querywidget.widget import QueryWidget


CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    QueryField(
        name='query',
        widget=QueryWidget(
            label="Search terms",
            description="""Define the search terms for the items you want to
            list by choosing what to match on.
            The list of results will be dynamically updated""",
        ),
        storage=atapi.AnnotationStorage(),
        validators=('javascriptDisabled',)
    ),
    StringField(
        name='sort_on',
        required=False,
        mode="rw",
        visible=False,
        default='sortable_title',
        widget=StringWidget(
                    label=_(u'Sort the collection on this index'),
                    description='',
                    visible=False,
                ),
        storage=atapi.AnnotationStorage(),
        ),
    StringField(
        name='sort_order',
        required=False,
        mode="rw",
        visible=False,
        default='ascending',
        widget=StringWidget(
                    label=_(u'The sort order, ascending or descending'),
                    description='',
                    visible=False,
                ),
        storage=atapi.AnnotationStorage(),
        ),
    BooleanField(
        name='limitNumber',
        required=False,
        mode="rw",
        default=False,
        widget=BooleanWidget(
            label=_(u'Limit Search Results'),
            description=_(u"If selected, only the 'Number of Items' "
                          u"indicated below will be displayed.")
        ),
        storage=atapi.AnnotationStorage(),
    ),
    IntegerField(
        name='itemCount',
        required=False,
        mode="rw",
        default=0,
        widget=IntegerWidget(
                    label=_(u'Number of Items'),
                    description=''
                ),
        storage=atapi.AnnotationStorage(),
        ),
    LinesField('customViewFields',
                required=False,
                mode="rw",
                default=('Title', 'Creator', 'Type', 'ModificationDate'),
                vocabulary='listMetaDataFields',
                enforceVocabulary=True,
                write_permission=ModifyPortalContent,
                widget=InAndOutWidget(
                        label=_(u'Table Columns'),
                        description=_(u"Select which fields to display when "
                                      u"'Display as Table' is checked.")
                        ),
                 ),
))

# Set storage on fields copied from ATDocumentSchema, making sure
# they work well with the python bridge properties.
CollectionSchema['title'].storage = atapi.AnnotationStorage()
CollectionSchema['description'].storage = atapi.AnnotationStorage()
CollectionSchema.moveField('query', after='description')

schemata.finalizeATCTSchema(
    CollectionSchema,
    folderish=False,
    moveDiscussion=False)


class Collection(document.ATDocument):
    """A Plone Collection"""
    implements(ICollection)
    ##TODO: do we need IDisabledExport as well?

    meta_type = "Collection"
    schema = CollectionSchema

    query = ATToolDependentFieldProperty('query')
    limitNumber = atapi.ATFieldProperty('limitNumber')
    itemCount = atapi.ATFieldProperty('itemCount')

    security = ClassSecurityInfo()

    security.declareProtected(View, 'listMetaDataFields')

    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog.
        """
        tool = getToolByName(self, ATCT_TOOLNAME)
        return tool.getMetadataDisplay(exclude)

    def results(self):
        if self.limitNumber:
            return self.query[:self.itemCount]
        return self.query

    def selectedViewFields(self):
        _mapping = {}
        for field in self.listMetaDataFields().items():
            _mapping[field[0]] = field
        return [_mapping[field] for field in self.customViewFields]

    def getFoldersAndImages(self):
        catalog = getToolByName(self, 'portal_catalog')
        folders = [item for item in self.results() if item.Type() == 'Folder']
        _mapping = {'folders': folders,
                    'images': {}}

        for folder in folders:
            query = {
                'portal_type': 'Image',
                'path': folder.getPath(),
            }
            _mapping['images'][folder.id] = IContentListing(catalog(query))

        _mapping['total_number_of_images'] = sum(map(len, _mapping['images'].values()))
        return _mapping

atapi.registerType(Collection, PROJECTNAME)
