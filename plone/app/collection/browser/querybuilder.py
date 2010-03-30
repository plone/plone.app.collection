from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry

from plone.app.collection import queryparser
from zope.component import getMultiAdapter, getUtility
from plone.app.collection.interfaces import ICollectionRegistryReader
from plone.app.contentlisting.interfaces import IContentListing
from Products.ATContentTypes import ATCTMessageFactory as _

import json

class ContentListingView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()

class QueryBuilder(BrowserView):
    """ This view is used by the javascripts, fetching configuration or results"""
    
    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def __call__(self, query):
        if self._results is None:
            self._results = self._makequery(query=query)
        return self._results

    def html_results(self, query):
        return getMultiAdapter((self(query), self.request), name='display_query_results')()

    def _makequery(self, query=None):
        parsedquery = queryparser.parseFormquery(self.context, query)
        if not parsedquery:
            return IContentListing([])
        return getMultiAdapter((self.context, self.request), name='searchResults')(query=parsedquery)

    def number_of_results(self, query):
        return "%s %s" % (len(self(query)), _("item(s) match your search term"))

class RegistryConfiguration(BrowserView):

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def __call__(self):
        return json.dumps(ICollectionRegistryReader(getUtility(IRegistry))())

        
