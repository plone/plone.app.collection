import logging

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces._content import IFolderish
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.archetypes import InplaceATItemMigrator
from Products.contentmigration.walker import CustomQueryWalker
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

logger = logging.getLogger('plone.app.collection')
prefix = "plone.app.querystring"

INVALID_OPERATION = 'Invalid operation %s for criterion: %s'
PROFILE_ID = 'profile-plone.app.collection:default'


def format_date(value):
    """Format the date.

    The value is expected to be a DateTime.DateTime object, though it
    actually also works on datetime.datetime objects.

    The query field expects a string with month/date/year.
    So 28 March 2013 should become '03/28/2013'.
    """
    return value.strftime('%m/%d/%Y')


def is_old_non_folderish_item(obj, **kwargs):
    """Is this an old not yet migrated Collection item?

    The old non-folderish and new folderish Collections have the same
    meta_type and portal_type, which means a simple catalog walker
    will crash when it is called on a new folderish Collection, for
    example when the upgrade step is run twice.  We can use this
    function to ignore the new Collections.
    """
    return not IFolderish(obj)


# Converters

class CriterionConverter(object):

    # Last part of the code for the dotted operation method,
    # e.g. 'string.contains'.
    operator_code = ''

    def get_query_value(self, value):
        # value may contain a query and some parameters, but in the
        # simple case it is simply a value.
        return value

    def get_operation(self, value):
        # Get dotted operation method.  This may depend on value.
        return "%s.operation.%s" % (prefix, self.operator_code)

    def __call__(self, formquery, criterion, registry):
        for index, value in criterion.getCriteriaItems():
            # Get the operation method.
            key = '%s.field.%s.operations' % (prefix, index)
            operations = registry.get(key)
            operation = self.get_operation(value)
            if not operation in operations:
                logger.error(INVALID_OPERATION % (operation, criterion))
                # TODO: raise an Exception?
                continue

            # Get the value that we will query for.
            query_value = self.get_query_value(value)

            # Add a row to the form query.
            row = {'i': index,
                   'o': operation}
            if query_value is not None:
                row['v'] = query_value
            formquery.append(row)


class ATDateCriteriaConverter(CriterionConverter):
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

    This code is based on the getCriteriaItems method from
    Products/ATContentTypes/criteria/date.py.  We check the field
    values ourselves instead of translating the values back and forth.
    """

    def __call__(self, formquery, criterion, registry):
        if criterion.value is None:
            return
        field = criterion.Field()
        value = criterion.Value()

        # Negate the value for 'old' days
        if criterion.getDateRange() == '-':
            value = -value

        date = DateTime() + value

        # Get the possible operation methods.
        key = '%s.field.%s.operations' % (prefix, field)
        operations = registry.get(key)

        def add_row(operation, value=None):
            if not operation in operations:
                raise ValueError(INVALID_OPERATION % (operation, criterion))
            # Add a row to the form query.
            row = {'i': field,
                   'o': operation}
            if value is not None:
                row['v'] = value
            formquery.append(row)

        operation = criterion.getOperation()
        if operation == 'within_day':
            if date.isCurrentDay():
                new_operation = "%s.operation.date.today" % prefix
                add_row(new_operation)
                return
            date_range = (date.earliestTime(), date.latestTime())
            new_operation = "%s.operation.date.between" % prefix
            add_row(new_operation, date_range)
            return
        elif operation == 'more':
            if value != 0:
                new_operation = "%s.operation.date.largerThanRelativeDate" % prefix
                add_row(new_operation, value)
                return
            else:
                new_operation = "%s.operation.date.afterToday" % prefix
                add_row(new_operation)
                return
        elif operation == 'less':
            if value != 0:
                new_operation = "%s.operation.date.lessThanRelativeDate" % prefix
                add_row(new_operation, value)
                return
            else:
                new_operation = "%s.operation.date.beforeToday" % prefix
                add_row(new_operation)
                return


class ATSimpleStringCriterionConverter(CriterionConverter):
    operator_code = 'string.contains'


class ATCurrentAuthorCriterionConverter(CriterionConverter):
    operator_code = 'string.currentUser'


class ATListCriterionConverter(CriterionConverter):
    operator_code = 'selection.is'

    def get_query_value(self, value):
        if value.get('operator') == 'and':
            logger.warn("Cannot handle selection operator 'and'. Using 'or'. "
                        "%r", value)
        return value['query']


class ATPathCriterionConverter(CriterionConverter):
    operator_code = 'string.path'

    def get_query_value(self, value):
        if value.get('depth') != -1:
            logger.warn("Cannot handle searching a path on a specific depth. "
                        "Allowing recursive search. %r", value)
        if not isinstance(value['query'], list):
            # Simple string.  I have not seen this yet in practice,
            # but it might happen.
            return value['query']
        # We have a list, but the string.path operator can currently
        # only handle one path, as a simple string.
        if len(value['query']) > 1:
            logger.warn("Multiple paths in query. Using only the first. %r",
                        value['query'])
        return value['query'][0]


class ATBooleanCriterionConverter(CriterionConverter):

    def get_operation(self, value):
        # Get dotted operation method.
        # value is one of these beauties:
        # value = [1, True, '1', 'True']
        # value = [0, '', False, '0', 'False', None, (), [], {}, MV]
        if True in value:
            code = 'isTrue'
        elif False in value:
            code = 'isFalse'
        else:
            logger.warn("Unknown value for boolean criterion. "
                        "Falling back to True. %r", value)
            code = 'isTrue'
        return "%s.operation.boolean.%s" % (prefix, code)

    def __call__(self, formquery, criterion, registry):
        for index, value in criterion.getCriteriaItems():
            # Get the operation method.
            if index == 'is_folderish':
                fieldname = 'isFolderish'
            elif index == 'is_default_page':
                fieldname = 'isDefaultPage'
            else:
                fieldname = index
            key = '%s.field.%s.operations' % (prefix, fieldname)
            try:
                operations = registry.get(key)
            except KeyError:
                logger.error("No operations available for index %s", fieldname)
                # TODO: raise an Exception?
                continue
            operation = self.get_operation(value)
            if not operation in operations:
                logger.error(INVALID_OPERATION % (operation, criterion))
                # TODO: raise an Exception?
                continue
            # Add a row to the form query.
            row = {'i': index,
                   'o': operation}
            formquery.append(row)


class ATDateRangeCriterionConverter(CriterionConverter):
    operator_code = 'date.between'

    def get_query_value(self, value):
        return value['query']


class ATPortalTypeCriterionConverter(CriterionConverter):
    operator_code = 'selection.is'


class TopicMigrator(ATItemMigrator):
    src_portal_type = 'Topic'
    src_meta_type = 'ATTopic'
    dst_portal_type = dst_meta_type = 'Collection'
    view_methods_mapping = {
        'folder_listing': 'standard_view',
        'folder_summary_view': 'summary_view',
        'folder_full_view': 'all_content',
        'folder_tabular_view': 'tabular_view',
        'atct_album_view': 'thumbnail_view',
        'atct_topic_view': 'standard_view',
        }

    @property
    def registry(self):
        return self.kwargs['registry']

    def last_migrate_layout(self):
        """Migrate the layout (view method).

        This needs to be done last, as otherwise our changes in
        migrate_criteria may get overriden by a later call to
        migrate_properties.
        """
        if self.old.getCustomView():
            # Previously, the atct_topic_view had logic for showing
            # the results in a list or in tabular form.  If
            # getCustomView is True, this means the new object should
            # use the tabular view.
            self.new.setLayout('tabular_view')
            return

        layout = self.view_methods_mapping.get(self.old.getLayout())
        if layout:
            self.new.setLayout(layout)

    def migrate_criteria(self):
        """Migrate old style to new style criteria.

        Plus handling for some special fields.
        """
        # The old Topic has boolean limitNumber and integer itemCount,
        # where the new Collection only has limit.
        if self.old.getLimitNumber():
            self.new.setLimit(self.old.getItemCount())

        # Get the old criteria.
        # See also Products.ATContentTypes.content.topic.buildQuery
        criteria = self.old.listCriteria()
        formquery = []
        for criterion in criteria:
            type_ = criterion.__class__.__name__
            if type_ == 'ATSortCriterion':
                # Sort order and direction are now stored in the Collection.
                self.new.setSort_reversed(criterion.getReversed())
                self.new.setSort_on(criterion.Field())
                logger.info("Sort on %r, reverse: %s.",
                            self.new.getSort_on(), self.new.getSort_reversed())
                continue

            converter = CONVERTERS.get(type_)
            if converter is None:
                msg = 'Unsupported criterion %s' % type_
                logger.error(msg)
                raise ValueError(msg)
            converter(formquery, criterion, self.registry)

        logger.info("formquery: %s" % formquery)
        self.new.setQuery(formquery)


class FolderishCollectionMigrator(InplaceATItemMigrator):
    src_portal_type = src_meta_type = 'Collection'
    dst_portal_type = dst_meta_type = 'Collection'


def migrate_to_folderish_collections(context):
    """Migrate new-style Collections to folderish Collections.

    This can be used as upgrade step.

    The new-style Collections started out as inheriting from
    ATDocument.  Historically users could nest topics, so we want to
    try to bring that back.  This is the first step: make existing
    new-style Collections folderish.

    TODO/notes:

    - This simple migration seems to work.

    - The sub collection should 'inherit' the query from its parent,
      otherwise this exercise does not make much sense.  See the
      maurits-recursive branch of archetypes.querywidget, which seems
      to work, though for the tests to pass it currently needs the
      maurits-upgradepath branch of plone.app.collection.

    """
    site = getToolByName(context, 'portal_url').getPortalObject()
    collection_walker = CustomQueryWalker(
        site, FolderishCollectionMigrator,
        callBefore=is_old_non_folderish_item)
    collection_walker.go()


def run_typeinfo_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')


def run_actions_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'actions')


def run_propertiestool_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'propertiestool')


def migrate_topics(context):
    """Migrate ATContentTypes Topics to plone.app.collection Collections.

    This can be used as upgrade step.

    The new-style Collections might again get some changes later.
    They may become folderish or dexterity items or dexterity
    containers or a dexterity behavior.

    For the moment this is just for the 1.x Collections.  Nested
    Topics cannot be migrated for the moment and may give an error.
    """
    site = getToolByName(context, 'portal_url').getPortalObject()
    topic_walker = CustomQueryWalker(site, TopicMigrator)
    # Parse the registry to get allowed operations and pass it to the
    # migrator.
    reg = getUtility(IRegistry)
    reader = IQuerystringRegistryReader(reg)
    registry = reader.parseRegistry()
    topic_walker.go(registry=registry)


CONVERTERS = {
    # Create an instance of each converter.
    'ATCurrentAuthorCriterion': ATCurrentAuthorCriterionConverter(),
    'ATDateCriteria': ATDateCriteriaConverter(),
    'ATListCriterion': ATListCriterionConverter(),
    'ATPathCriterion': ATPathCriterionConverter(),
    'ATSimpleStringCriterion': ATSimpleStringCriterionConverter(),
    'ATBooleanCriterion': ATBooleanCriterionConverter(),
    'ATDateRangeCriterion': ATDateRangeCriterionConverter(),
    'ATPortalTypeCriterion': ATPortalTypeCriterionConverter(),
    # TODO:
    #'ATReferenceCriterion',
    #'ATRelativePathCriterion',
    #'ATSelectionCriterion',
    #'ATSimpleIntCriterion',
    }
