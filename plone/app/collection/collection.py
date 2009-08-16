"""Definition of the Collection content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata

from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME

from archetypes.querystringwidget.widget import QueryStringWidget



CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='querystring',
        default="",
        widget=QueryStringWidget(
            label='Querystring',
            description = "Querystring as used by plone.app.search",
        ),
    ),

))

# Set storage on fields copied from ATDocumentSchema, making sure
# they work well with the python bridge properties.

CollectionSchema['title'].storage = atapi.AnnotationStorage()
CollectionSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    CollectionSchema,
    folderish=False,
    moveDiscussion=False
)

class Collection(document.ATDocument):
    """A Plone collection"""
    implements(ICollection)

    meta_type = "Collection"
    schema = CollectionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Collection, PROJECTNAME)
