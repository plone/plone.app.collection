"""
    Definition of the Collection content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import InAndOutWidget
from Products.Archetypes.fieldproperty import ATToolDependentFieldProperty
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME
from plone.app.collection.config import TOOLNAME
from plone.app.collection import PloneMessageFactory as _
from archetypes.querywidget.field import QueryField
from archetypes.querywidget.widget import QueryWidget
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.permissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

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
                default=('Title',),
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
        tool = getToolByName(self, TOOLNAME)
        return tool.getMetadataDisplay(exclude)

atapi.registerType(Collection, PROJECTNAME)
