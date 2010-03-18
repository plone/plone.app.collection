from collections import namedtuple
from copy import deepcopy

from Acquisition import aq_parent
from DateTime import DateTime
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

Row = namedtuple('Row', ['index', 'operator', 'values'])


class QueryParser(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def parseFormquery(self, formquery):
        if not formquery:
            return {}
        reg = getUtility(IRegistry)

        # make sure the things in formquery are dicts, not crazy things
        formquery = map(dict, formquery)

        formquery = deepcopy(formquery)
        query = {}
        for row in formquery:

            operator = row.get('o', None)
            function_path = reg["%s.operation" % operator]

            # The functions expect this pattern of object, so lets give it to
            # them in a named tuple instead of jamming things onto the request
            row = Row(index=row.get('i', None),
                      operator=function_path,
                      values=row.get('v', None))

            kwargs = {}

            module, function = row.operator.split(":")
            fromlist = module.split(".")[:-1]
            try:
                module = __import__(module, fromlist=fromlist)
                parser = getattr(module, function)
            except (ImportError, AttributeError):
                raise  # XXX: Be more friendly
            else:
                kwargs = parser(self.context, row)

            query.update(kwargs)

        if not query:
            # If the query is empty fall back onto the equality query
            query = _equal(self.context, row)

        return query


# operators
# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=Creator&query.o:records=plone.app.collection.operation.string.is&query.v:records=admin
# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=Creator&query.o:records=plone.app.collection.operation.string.is&query.v:records=joshenken
def _equal(context, row):
    return {row.index: {'query': row.values, }}


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.between&query.v:records:list=2010/03/18&query.v:records:list=2010/03/19
def _between(context, row):
    tmp = {row.index: {
              'query': row.values,
              'range': 'minmax',
              },
          }
    return tmp


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.largerThan&query.v:records=2010/03/18
def _largerThan(context, row):
    tmp = {row.index: {
              'query': row.values,
              'range': 'min',
              },
          }
    return tmp


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.lessThan&query.v:records=2010/03/18
def _lessThan(context, row):
    tmp = {row.index: {
              'query': row.values,
              'range': 'max',
              },
          }
    return tmp


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=Creator&query.o:records=plone.app.collection.operation.string.currentUser
# Anonymous users are represented by the 'Anonymous User' username. Normally there will not be any results for that user.
def _currentUser(context, row):
    mt = getToolByName(context, 'portal_membership')
    user = mt.getAuthenticatedMember()
    username = 'Anonymous User'
    if user:
        username = user.getUserName()

    return {row.index: {
              'query': username,
              },
          }


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.lessThanRelativeDate&query.v:records=-1
# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.lessThanRelativeDate&query.v:records=1
def _lessThanRelativeDate(context, row):
    # values is the number of days
    values = int(row.values)

    now = DateTime()
    my_date = now + values

    my_date = my_date.earliestTime()
    row = Row(index=row.index,
              operator=row.operator,
              values=my_date)

    return _lessThan(context, row)


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.moreThanRelativeDate&query.v:records=-1
# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=modified&query.o:records=plone.app.collection.operation.date.moreThanRelativeDate&query.v:records=1
def _moreThanRelativeDate(context, row):
    values = int(row.values)

    now = DateTime()
    my_date = now + values

    my_date = my_date.latestTime()
    row = Row(index=row.index,
              operator=row.operator,
              values=my_date)

    return _largerThan(context, row)


# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=path&query.o:records=plone.app.collection.operation.string.path&query.v:records=/news/
# http://localhost:8080/Plone/@@querybuilder_html_results?query.i:records=path&query.o:records=plone.app.collection.operation.string.path&query.v:records=718f66a14bda3688d64bb36309e0d76e
def _path(context, row):
    values = row.values

    # UID
    if not '/' in values:
        values = getPathByUID(context, values)

    tmp = {row.index: {'query': values, }}

    # XXX: support this
    depth = getattr(row, 'depth', None)
    if depth is not None:  # could be 0
        tmp[row.index]['depth'] = int(depth)
    return tmp


# http://localhost:8080/Plone/news/aggregator/@@querybuilder_html_results?query.i:records=path&query.o:records=plone.app.collection.operation.string.relativePath&query.v:records=../
def _relativePath(context, row):
    t = len([x for x in row.values.split('/') if x])

    obj = context
    for x in xrange(t):
        obj = aq_parent(obj)

    row = Row(index=row.index,
              operator=row.operator,
              values='/'.join(obj.getPhysicalPath()))

    return _path(context, row)


# Helper functions
def getPathByUID(context, uid):
    """Returns the path of an object specified by UID"""

    reference_tool = getToolByName(context, 'reference_catalog')
    obj = reference_tool.lookupObject(uid)

    if obj:
        return '/'.join(obj.getPhysicalPath())

    return ""
