"""
    Query Widget
"""

__author__  = 'Maarten Kling <maarten@fourdigits.nl>, Ralph Jacobs <ralph@fourdigits.nl>'
__docformat__ = 'epytext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from zope.component import getMultiAdapter

from browser.config import CRITERION, SORTABLES


class QueryWidget(TypesWidget):
    """QueryWidget"""

    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'querywidget',
        }),

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """A custom implementation for the widget form processing."""
        value = form.get(field.getName())
        if value:
            return value, {}

    def getConfig(self):
        return {'indexes':CRITERION, 'sortable_indexes': SORTABLES}
        # we wrap this in a dictionary so we can add more configuration data
        # to the payload in the future. This is data that will be fetched
        # by a browser AJAX call


    def previewSearchResults(self, request, context):
        return getMultiAdapter((context, request),name='querybuilderpreviewresults')()

    def SearchResults(self, request, context):
        return getMultiAdapter((context, request),name='querybuilderpreviewresults')()

__all__ = ('QueryWidget')

registerWidget(QueryWidget,
               title='Query',
               description=('Field for storing collection query'),
               used_for=('plone.app.collection.QueryField',)
               )
