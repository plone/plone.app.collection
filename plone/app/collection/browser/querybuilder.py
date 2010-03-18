from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from config import CRITERION, SORTABLES
from plone.app.collection.queryparser import QueryParser
from zope.component import getMultiAdapter, getUtility
from plone.app.collection.interfaces import ICollectionRegistryReader
from plone.app.contentlisting.interfaces import IContentListing
import json

class ContentListingView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()

class QueryBuilder(BrowserView):
    """This view assembles the query and fetches results"""
    
    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def __call__(self, query=None):
        if self._results is None:
            self._results = self._queryForResults(query=query)
        return self._results

    def html_results(self):
        return getMultiAdapter((self(), self.request), name='display_query_results')()

    def _queryForResults(self, query=None):
        queryparser = QueryParser(self.context, self.request)
        parsedquery = queryparser.parseFormquery(query)
        if not parsedquery:
            return IContentListing([])
        # sorting
        #query['sort_on'] = getattr(self.request, 'sort_on', 'getId')
        #query['sort_order'] = getattr(self.request, 'sort_order', 'ascending')
        #NO WAY are we pulling these from the request. Let's pass them explicitly.
        
        #fetch and return the actual resultset from plone.app.contentlisting
        return getMultiAdapter((self.context, self.request), name='searchResults')(query=parsedquery)

    def getNumberOfResults(self):
        return len(self())

    def getConfig(self):
        return {'indexes': CRITERION, 'sortable_indexes': SORTABLES}
        #tmp = self.getConfigFromRegistry()
        #tmp['sortable_indexes'] = config.SORTABLES
        #return tmp

    def getJSONConfig(self):
        return json.dumps(self.getConfig())

    def getConfigFromRegistry(self):
        """Returns the indexes and sortable indexes from the portal registry"""
        return ICollectionRegistryReader(getUtility(IRegistry))()

    def getJSONConfigFromRegistry(self):
        """returns the portal registry settings in JSON format"""
        return json.dumps(self.getConfigFromRegistry())
