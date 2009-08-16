from plone.app.search.browser import AdvancedSearch

class CriterionEditFrom(AdvancedSearch):

    def __init__(self, context, request):
        self._results = None
        self.context = context
        self.request = request
