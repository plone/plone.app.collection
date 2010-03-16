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
