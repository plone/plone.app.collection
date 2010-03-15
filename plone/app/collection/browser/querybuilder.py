from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from config import CRITERION, SORTABLES
import json
from plone.app.collection.queryparser import QueryParser
from zope.component import queryMultiAdapter, getMultiAdapter
from ZTUtils import make_query

class QueryBuilder(object):
    """ """

    # This is the advanced search that uses the query view from new-style-collections.
    # If we end up not using this view for advanced search, it should probably be moved to the collections
    # package
    _results = None

    def getNumberOfResults(self, request):
        return len(self.results(request))

    def getFormattedNumberOfResults(self, request):
        return "%d items remaining" % (len(self.results(request)))

    def results(self, request):
        if self._results is None:
            self._results = self._queryForResults(request)
        return self._results

    def _queryForResults(self, request, formquery=None):
        # parse query
        if not formquery:
            formquery=self.request.get('query', None)
        queryparser=QueryParser(self.context, self.request)
        query = queryparser.parseFormquery(formquery)

        if not query:
            return IContentListing([])

        # sorting
        query['sort_on'] = getattr(self.request, 'sort_on', 'getObjPositionInParent')
        query['sort_order'] = getattr(self.request, 'sort_order', 'ascending')

        # Get me my stuff!
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)

        if results:
            return IContentListing(results)
        return IContentListing([])

    def getConfig(self):
        return {'indexes':CRITERION, 'sortable_indexes': SORTABLES}
        # we wrap this in a dictionary so we can add more configuration data
        # to the payload in the future. This is data that will be fetched
        # by a browser AJAX call

    def getJSONConfig(self):
        return json.dumps(self.getConfig())

    def previewSearchResults(self, request, context):
        return getMultiAdapter((context, request),name='querybuilderpreviewresults')()
