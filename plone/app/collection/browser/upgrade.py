import logging

from Products.CMFCore.utils import getToolByName
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

logger = logging.getLogger('plone.app.collection')
prefix = "plone.app.querystring"

INVALID_OPERATION = 'Invalid operation %s for criterion: %s'


class Erreur(object):
    def __init__(self, ob, exception=None, traceback=None, messages=None):
        self.ob = ob
        self.exception = exception
        self.traceback = traceback
        self.messages = messages

    def getStacktrace(self):
        if not self.traceback:
            return ""

        def format(line):
            return "Module %s, line %s, in %s, %s" % line
        return map(format, self.traceback)


def format_date(value):
    """Format the date.

    The value is expected to be a DateTime.DateTime object, though it
    actually also works on datetime.datetime objects.

    The query field expects a string with month/date/year.
    So 28 March 2013 should become '03/28/2013'.
    """
    return value.strftime('%m/%d/%Y')


# Convertors
# TODO: make this class based so the individual convertors can be
# smaller as they are a lot alike.

def ATDateCriteria(formquery, criterion, registry):
    """Handle date criteria.

    Note that there is also ATDateRangeCriterion, which is much
    simpler as it just has two dates.

    In our case we have these valid operations:

    ['plone.app.querystring.operation.date.lessThan',
     'plone.app.querystring.operation.date.largerThan',
     'plone.app.querystring.operation.date.between',
     'plone.app.querystring.operation.date.lessThanRelativeDate',
     'plone.app.querystring.operation.date.largerThanRelativeDate',
     'plone.app.querystring.operation.date.today',
     'plone.app.querystring.operation.date.beforeToday',
     'plone.app.querystring.operation.date.afterToday']

    TODO: We may want to copy code from the getCriteriaItems method of
    Products/ATContentTypes/criteria/date.py and check the field
    values ourselves instead of translating the values back and forth.

    Note: this is probably the hardest criterion.
    """
    operator = {'max': 'lessThan',
                'min': 'largerThan',
                'min:max': 'between',
                }
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.date.%s" % (prefix, operator[value['range']])

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        if isinstance(value['query'], tuple):
            # TODO: if one of these dates is today/now (use the
            # isCurrentDay method to check this) then that probably
            # means we should use a different operator instead.
            query_value = [format_date(v) for v in value['query']]
        else:
            query_value = format_date(value['query'])
        row = {'i': index,
               'o': operation,
               'v': query_value}
        formquery.append(row)
    return messages


def ATSimpleStringCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.string.contains" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value}
        formquery.append(row)
    return messages


def ATCurrentAuthorCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.string.currentUser" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value}
        formquery.append(row)
    return messages


def ATListCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        key = '%s.field.%s.operations' % (prefix, index)
        operations = registry.get(key)
        operation = "%s.operation.list.contains" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value['query']}
        formquery.append(row)
    return messages


class TopicMigrator(ATItemMigrator):
    src_portal_type = 'Topic'
    src_meta_type = 'ATTopic'
    dst_portal_type = dst_meta_type = 'Collection'

    def migrate_criteria(self):
        messages = []  # TODO just use logging.

        # The old Topic has boolean limitNumber and integer itemCount,
        # where the new Collection only has limit.
        if self.old.getLimitNumber():
            self.new.setLimit(self.old.getItemCount())
        # TODO: Check the other fields, like sorting.  Might be taken
        # care of already.

        # Get the old criteria.
        # See also Products.ATContentTypes.content.topic.buildQuery
        criteria = self.old.listCriteria()
        formquery = []
        for criterion in criteria:
            type_ = criterion.__class__.__name__
            module = 'plone.app.collection.browser.upgrade'
            fromlist = module.split(".")[:-1]
            try:
                # TODO: Make 'module' a class attribute.
                module = __import__(module, fromlist=fromlist)
                convertor = getattr(module, type_)
            except (ImportError, AttributeError):
                messages.append('Unsupported criterion %s' % type_)
                continue
            else:
                # TODO: the registry is the same for every object, so
                # we may want to make this available as
                # self.parsed_registry.
                reg = getUtility(IRegistry)
                reader = IQuerystringRegistryReader(reg)
                result = reader.parseRegistry()

                messages_ = convertor(formquery, criterion, result)
                messages.extend(messages_)

        logger.info("formquery: %s" % formquery)
        self.new.setQuery(formquery)


def migrate_topics(context):
    """Migrate ATContentTypes Topics to plone.app.contenttypes Collections.

    This can be used as upgrade step.

    The new-style Collections might again get some changes later.
    They may become folderish or dexterity items or dexterity
    containers or a dexterity behavior.

    For the moment this is just for the 1.x Collections.  Nested
    Topics cannot be migrated for the moment and may give an error.
    """
    site = getToolByName(context, 'portal_url').getPortalObject()
    topic_walker = CatalogWalker(site, TopicMigrator)
    # TODO: we could parse the registry and pass it as keyword
    # argument to the 'go' method and use a custom migrator, to save
    # recalculating it again and again.
    topic_walker.go()
