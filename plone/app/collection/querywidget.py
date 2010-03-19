"""
    Query Widget
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from zope.component import getMultiAdapter

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from plone.app.collection.interfaces import ICollectionRegistryReader


class QueryWidget(TypesWidget):
    """QueryWidget"""

    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'querywidget',
        'helper_css': ('++resource++plone.app.collection.stylesheets/querywidget.css',),
        'helper_js': ('++resource++plone.app.collection.javascripts/querywidget.js',),
        }),

    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """A custom implementation for the widget form processing."""
        value = form.get(field.getName())
        # check if form.button.addcriteria, or removecriteria is in request
        # this only happends when javascript is disabled
        removeresult = [x for x in form if x.find('removecriteria') == 0]
        if 'form.button.addcriteria' in form or removeresult:
            return {}, {}
        if value:
            return value, {}

    def getConfig(self):
        """get the config"""
        registry = getUtility(IRegistry)
        registryreader = ICollectionRegistryReader(registry)
        config = registryreader()
        return config

    def SearchResults(self, request, context, accessor):
        """search results"""
        return getMultiAdapter((accessor(), request), name='display_query_results')()


__all__ = ('QueryWidget')

registerWidget(QueryWidget,
               title='Query',
               description=('Field for storing collection query'),
               used_for=('plone.app.collection.QueryField',))
