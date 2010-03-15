"""
    QueryField field class
"""

from __future__ import nested_scopes

__docformat__ = 'epytext'
__author__ = 'Maarten Kling <maarten@fourdigits.nl>, Ralph Jacobs <ralph@fourdigits.nl>'


from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import registerField
from plone.app.collection.interfaces import IQueryField
from zope.interface import implements


class QueryField(ObjectField):
    """QueryField for storing query"""
    implements(IQueryField)
    _properties = ObjectField._properties.copy()

    security = ClassSecurityInfo()

    def __init__(self, name=None, **kwargs):
        """ Create QueryField instance"""
        # call super constructor
        ObjectField.__init__(self, name, **kwargs)

registerField(QueryField,
              title='QueryField',
              description=('query field for storing collection query'))
