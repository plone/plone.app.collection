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
                raise # XXX: Be more friendly
            else:
                kwargs = parser(self.context, row)

            query.update(kwargs)
        
        if not query:
            # If the query is empty fall back onto the equality query
            query = _equal(self.context, row)
        
        return query

# operators
def _equal(context, row):
    return {row.index: {
                'query':row.values
                }
             }

# query.i:records=modified&query.o:records=between&query.v:records:list=2009/08/12&query.v:records:list=2009/08/14
# v[0] >= x > v[1]
def _between(context, row):
    tmp = {row.index: {
              'query':row.values,
              'range':'minmax',
              },
          }
    return tmp
        
# query.i:records=modified&query.o:records=larger_then_or_equal&query.v:records=2009/08/12
# x >= value
def _largerThan(context, row):
    tmp = {row.index: {
              'query':row.values,
              'range':'min',
              },
          }
    return tmp

# query.i:records=modified&query.o:records=less_then&query.v:records=2009/08/14
# x < value
def _lessThan(context, row):
    tmp = {row.index: {
              'query':row.values,
              'range':'max',
              },
          }
    return tmp
    
# current user
def _currentUser(context, row):
    tmp = {row.index: {
              'query': getCurrentUsername(context),
              },
          }
    return tmp

# query.i:records=modified&query.o:records=less_then_relative_date&query.v:records=-7
def _lessThanRelativeDate(context, row):
    values = int(row.values)

    now = DateTime()
    my_date = now + values
    
    my_date = my_date.earliestTime()
    row.values = my_date
    return _lessThan(context, row)

# query.i:records=modified&query.o:records=more_then_relative_date&query.v:records=-2
def _moreThanRelativeDate(context, row):
    values=int(row.values)

    now = DateTime()
    my_date = now + values
    
    my_date = my_date.latestTime()
    row.values = my_date
    return _largerThanOrEqual(context, row)

# query.i:records=path&query.o:records=path&query.v:records=/search/news/
# query.i:records=path&query.o:records=path&query.v:records=08fb402c83d0e68cf4d547ea79f7680c
def _path(context, row):
    values = row.values
    
    # UID
    if not '/' in values:
        row.values = getPathByUID(values) # XXX : This looks broken
    
    tmp={row.index:{
        'query':row.values
    }}
    
    depth = getattr(row, 'depth', None)
    if depth is not None: # can be 0
        tmp[row.index]['depth'] = int(depth)
    return tmp
    
# query.i:records=path&query.o:records=relative_path&query.v:records=../../..
def _relativePath(context, row):
    t = len([x for x in row.values.split('/') if x])
    
    obj = context
    for x in xrange(t):
        obj = aq_parent(obj)

    if obj and hasattr(obj, 'getPhysicalPath'):
        row.values = '/'.join(obj.getPhysicalPath())
        return _path(context, row)
    
    row.values = '/'.join(obj.getPhysicalPath())
    return _path(context, row)
    
# Helper methods
def getCurrentUsername(context):
    mt = getToolByName(context, 'portal_membership')
    user = mt.getAuthenticatedMember()
    if user:
        return user.getUserName()
    return ''

def getPathByUID(context):
    """Returns the path of an object specified in the request by UID"""

    request = context.REQUEST

    if not hasattr(request, 'uid'):
    	return ""

    uid = request['uid']

    reference_tool = getToolByName(context, 'reference_catalog')
    obj = reference_tool.lookupObject(uid)

    if obj:
    	return obj.absolute_url()

    return ""