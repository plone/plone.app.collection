from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry

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

    def __call__(self, query):
        if self._results is None:
            self._results = self._queryForResults(query=query)
        return self._results

    def html_results(self, query):
        return getMultiAdapter((self(query), self.request), name='display_query_results')()

    def _queryForResults(self, query=None):
        queryparser = QueryParser(self.context, self.request)
        parsedquery = queryparser.parseFormquery(query)
        if not parsedquery:
            return IContentListing([])
        return getMultiAdapter((self.context, self.request), name='searchResults')(query=parsedquery)

    def getNumberOfResults(self, query):
        return len(self(query))

    # Fetch configuration

    def getConfig(self):
        config = self.getConfigFromRegistry()
        return config

    def getJSONConfig(self):
        return json.dumps(self.getConfig())

    def getConfigFromRegistry(self):
        """Returns the indexes and sortable indexes from the portal registry"""
        return ICollectionRegistryReader(getUtility(IRegistry))()

    def getJSONConfigFromRegistry(self):
        """returns the portal registry settings in JSON format"""
        return json.dumps(self.getConfigFromRegistry())
