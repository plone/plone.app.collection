from Products.Five.browser import BrowserView
from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import log
from config import CRITERION, SORTABLES
from plone.app.collection.queryparser import QueryParser
from zope.component import queryMultiAdapter, getMultiAdapter
from ZTUtils import make_query
from zope.component import getUtility
from plone.app.collection.registryreader import CollectionRegistryReader
import json

class QueryBuilder(BrowserView):
    """ """

    # This is the advanced search that uses the query view from new-style-collections.
    # If we end up not using this view for advanced search, it should probably be moved to the collections
    # package

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request


    def __call__(self,value=None):
        """Call"""
        self.value = value
        return self.index()


    def getNumberOfResults(self):
        return len(self.results())

    def getFormattedNumberOfResults(self):
        return "%d items remaining" % (len(self.results()))

    def results(self):
        if self._results is None:
            self._results = self._queryForResults()
        return self._results

    def _queryForResults(self, formquery=None):

        if formquery is None:
            if 'query' in self.request.form:
                formquery = self.request.form.get('query', None)
            else:
                formquery = self.value
        
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

    def getConfigFromRegistry(self):
        """Returns the indexes and sortable indexes from the portal registry"""
        registry = getUtility(IRegistry)
        registryreader = CollectionRegistryReader(registry)
        result = registryreader()
        return result

    def getJSONConfigFromRegistry(self):
        """returns the portal registry settings in JSON format"""
        return json.dumps(self.getConfigFromRegistry())

    def previewSearchResults(self):
        return getMultiAdapter((self.context, self.request),name='querybuilderpreviewresults')()
