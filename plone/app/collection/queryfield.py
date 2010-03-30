"""
    QueryField field class
"""

from __future__ import nested_scopes

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import registerField
from plone.app.collection.interfaces import IQueryField
from zope.interface import implements
from zope.app.component.hooks import getSite

from plone.app.collection.browser.querybuilder import QueryBuilder

class QueryField(ObjectField):
    """QueryField for storing query"""
    implements(IQueryField)
    _properties = ObjectField._properties.copy()

    security = ClassSecurityInfo()

    def __init__(self, name=None, **kwargs):
        """ Create QueryField instance"""
        # call super constructor
        ObjectField.__init__(self, name, **kwargs)

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    def set(self, instance, value, **kwargs):
        """
        The passed in object should be a records object, or a sequence of dictionaries
        """
        ObjectField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        """Get the query dict from the request or from the object"""
        raw = kwargs.get('raw', None)
        value = self.getRaw(instance)
        if raw == True:
            # We actually wanted the raw value, should have called getRaw
            return value
        querybuilder = QueryBuilder(instance, getSite().REQUEST)
        return querybuilder(value)
    
    def getRaw(self, instance, **kwargs):
        return ObjectField.get(self, instance, **kwargs) or ()


registerField(QueryField,
              title='QueryField',
              description=('query field for storing collection query'))
