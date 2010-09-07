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

    def __call__(self, **kw):
        return self.index(**kw)


class QueryBuilder(BrowserView):
    """ This view is used by the javascripts,
        fetching configuration or results"""

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def __call__(self, query):
        if self._results is None:
            self._results = self._makequery(query=query)
        return self._results

    def html_results(self, query):
        options = dict(original_context=self.context)
        return getMultiAdapter((self(query), self.request),
            name='display_query_results')(
            **options)

    def _makequery(self, query=None):
        parsedquery = queryparser.parseFormquery(self.context, query)
        if not parsedquery:
            return IContentListing([])
        return getMultiAdapter((self.context, self.request),
            name='searchResults')(query=parsedquery)

    def number_of_results(self, query):
        return _(u"batch_x_items_matching_your_criteria",
                 default=u"${number} items matching your search terms",
                 mapping={'number': len(self(query))})


class RegistryConfiguration(BrowserView):

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def __call__(self):
        return json.dumps(ICollectionRegistryReader(getUtility(IRegistry))())
