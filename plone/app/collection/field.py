from copy import deepcopy
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import registerField
from zope.interface import implements
from zope.interface import Interface
from zope.site.hooks import getSite
from plone.app.querystring.querybuilder import QueryBuilder


class IQueryField(Interface):
    """Query field interface """


class QueryField(ObjectField):
    """QueryField for storing query"""

    implements(IQueryField)
    _properties = ObjectField._properties.copy()

    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        """Get the query dict from the request or from the object"""
        raw = kwargs.get('raw', None)
        value = self.getRaw(instance)
        if raw == True:
            # We actually wanted the raw value, should have called getRaw
            return value
        querybuilder = QueryBuilder(instance, getSite().REQUEST)

        sort_on = kwargs.get('sort_on', instance.getSort_on())
        sort_order = 'reverse' if instance.getSort_reversed() else 'ascending'
        limit = kwargs.get('limit', instance.getLimit())
        return querybuilder(query=value, batch=kwargs.get('batch', False),
            b_start=kwargs.get('b_start', 0), b_size=kwargs.get('b_size', 30),
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=kwargs.get('brains', False),
            custom_query=kwargs.get('custom_query', {}))

    def getRaw(self, instance, **kwargs):
        return deepcopy(ObjectField.get(self, instance, **kwargs) or [])


registerField(QueryField, title='QueryField',
    description=('query field for storing a query'))
