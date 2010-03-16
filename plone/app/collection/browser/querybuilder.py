from Products.Five.browser import BrowserView
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from config import CRITERION, SORTABLES
import json
from plone.app.collection.queryparser import QueryParser
from zope.component import queryMultiAdapter, getMultiAdapter
from ZTUtils import make_query

class QueryBuilder(BrowserView):
    """ """

    # This is the advanced search that uses the query view from new-style-collections.
    # If we end up not using this view for advanced search, it should probably be moved to the collections
    # package

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def getNumberOfResults(self):
        return len(self.results())

    def getFormattedNumberOfResults(self):
        return "%d items remaining" % (len(self.results()))

    def results(self):
        if self._results is None:
            self._results = self._queryForResults()
        return self._results

    def _queryForResults(self, formquery=None):
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

        #fetch and return the actual resultset
        return getMultiAdapter((self.context, self.request), name='searchResults')(query=query)


    def getConfig(self):
        return {'indexes':CRITERION, 'sortable_indexes': SORTABLES}
        # we wrap this in a dictionary so we can add more configuration data
        # to the payload in the future. This is data that will be fetched
        # by a browser AJAX call

    def getJSONConfig(self):
        return json.dumps(self.getConfig())

    def previewSearchResults(self):
        return getMultiAdapter((self.context, self.request),name='querybuilderpreviewresults')()
