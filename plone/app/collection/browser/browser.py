from querybuilder import QueryBuilder
from plone.app.collection.interfaces import ICollection
from Products.CMFPlone.utils import log


class CriterionEditFrom(QueryBuilder):

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request


class CollectionViews(QueryBuilder):
    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request

    def results(self):
        return ''
        formquery= ''## get the current field here
        if self._results is None:
            self._results = self._queryForResults(formquery)
        return self._results
