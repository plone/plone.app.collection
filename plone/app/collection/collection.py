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
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME
from plone.app.collection.config import TOOLNAME
from Products.ATContentTypes import ATCTMessageFactory as _
from queryfield import QueryField
from querywidget import QueryWidget
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.permissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    QueryField(
        name='query',
        widget=QueryWidget(
            label="Search terms",
            description="""Define the search terms for the items you want to list by choosing what to match on.
            The list of results will be dynamically updated""",
        ),
        validators=('javascriptDisabled',)
    ),
    BooleanField(
        name='limitNumber',
        required=False,
        mode="rw",
        default=False,
        widget=BooleanWidget(
            label=_(u'label_limit_number',
                    default=u'Limit Search Results'),
            description=_(u'help_limit_number',
                          default=u"If selected, only the 'Number of Items' "
                                   "indicated below will be displayed.")
        ),
    ),
    IntegerField(
        name='itemCount',
            required=False,
            mode="rw",
            default=0,
            widget=IntegerWidget(
                    label=_(u'label_item_count', default=u'Number of Items'),
                    description=''
                    ),
             ),
    BooleanField('customView',
                required=False,
                mode="rw",
                default=False,
                write_permission = ModifyPortalContent,
                widget=BooleanWidget(
                        label=_(u'label_custom_view', default=u'Display as Table'),
                        description=_(u'help_custom_view',
                                      default=u"Columns in the table are controlled "
                                               "by 'Table Columns' below.")
                        ),
                 ),
    LinesField('customViewFields',
                required=False,
                mode="rw",
                default=('Title',),
                vocabulary='listMetaDataFields',
                enforceVocabulary=True,
                write_permission = ModifyPortalContent,
                widget=InAndOutWidget(
                        label=_(u'label_custom_view_fields', default=u'Table Columns'),
                        description=_(u'help_custom_view_fields',
                                      default=u"Select which fields to display when "
                                               "'Display as Table' is checked.")
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

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security = ClassSecurityInfo()

    security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog.
        """
        tool = getToolByName(self, TOOLNAME)
        return tool.getMetadataDisplay(exclude)

atapi.registerType(Collection, PROJECTNAME)
