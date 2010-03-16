"""
    Definition of the Collection content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME

from queryfield import QueryField
from querywidget import QueryWidget

CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    QueryField(
        name='query',
        widget=QueryWidget(
            label="Query 1",
            description="Query for the collection",
        ),
    ),
    QueryField(
        name='query2',
        widget=QueryWidget(
            label="Query 2",
            description="Query for the collection",
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
    moveDiscussion=False)


class Collection(document.ATDocument):
    """A Plone Collection"""
    implements(ICollection)

    meta_type = "Collection"
    schema = CollectionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')


atapi.registerType(Collection, PROJECTNAME)
