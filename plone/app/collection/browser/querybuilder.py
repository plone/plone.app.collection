from Products.Five.browser import BrowserView
from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
#from Products.CMFCore.utils import getToolByName
#from Products.CMFPlone.utils import log
from config import CRITERION, SORTABLES
#from config import SORTABLES
#import config
from plone.app.collection.queryparser import QueryParser
#from zope.component import queryMultiAdapter, getMultiAdapter
from zope.component import getMultiAdapter
#from ZTUtils import make_query
from zope.component import getUtility
from plone.app.collection.interfaces import ICollectionRegistryReader
import json


class ContentListingView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()


class QueryBuilder(BrowserView):
    """ """

    def __init__(self, context, request):
        self.value = None
        self._results = None
        self.context = context
        self.request = request

    def __call__(self, value=None):
        self.value = value
        return self.results()

    def results(self, formquery=None):
        if self._results is None:
            self._results = self._queryForResults(formquery=formquery)
        return self._results

    def html_results(self):
        return getMultiAdapter((self.results(), self.request), name='display_query_results')()

    def _queryForResults(self, formquery=None):

        if formquery is None:
            if 'query' in self.request.form:
                formquery = self.request.form.get('query', None)
            else:
                formquery = self.value

        queryparser = QueryParser(self.context, self.request)
        query = queryparser.parseFormquery(formquery)
        if not query:
            return IContentListing([])

        # sorting
        query['sort_on'] = getattr(self.request, 'sort_on', 'getObjPositionInParent')
        query['sort_order'] = getattr(self.request, 'sort_order', 'ascending')

        #fetch and return the actual resultset
        return getMultiAdapter((self.context, self.request), name='searchResults')(query=query)

    def getNumberOfResults(self):
        return len(self.results())

    def getConfig(self):
        return {'indexes': CRITERION, 'sortable_indexes': SORTABLES}
        #tmp = self.getConfigFromRegistry()
        #tmp['sortable_indexes'] = config.SORTABLES
        #return tmp

    def getJSONConfig(self):
        return json.dumps(self.getConfig())

    def getConfigFromRegistry(self):
        """Returns the indexes and sortable indexes from the portal registry"""
        registry = getUtility(IRegistry)
        registryreader = ICollectionRegistryReader(registry)
        result = registryreader()
        return result

    def getJSONConfigFromRegistry(self):
        """returns the portal registry settings in JSON format"""
        return json.dumps(self.getConfigFromRegistry())
