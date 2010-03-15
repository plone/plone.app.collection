"""
    Definition of the Collection content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from plone.app.collection.interfaces import ICollection
from plone.app.collection.config import PROJECTNAME

from QueryField import QueryField
from QueryWidget import QueryWidget

CollectionSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    QueryField(
        name='query',
        widget=QueryWidget(
            label="Query",
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

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    def getQueryDict(self):
        """Get the query dict from the request or from the object"""
        # Try the request to be current
        query = getattr(self.REQUEST, 'query', None)
        if query:
            return query
        # Try the stored dict
        query = getattr(self, 'querydict', None)
        if query:
            return query

        # Nothing here. Should I raise an exception?
        return {}

atapi.registerType(Collection, PROJECTNAME)
