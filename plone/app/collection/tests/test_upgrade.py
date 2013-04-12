from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login

from .base import CollectionMigrationTestCase
from plone.app.collection.upgrade import migrate_topics


class TestCriterionConverters(CollectionMigrationTestCase):

    def run_migration(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        migrate_topics(getToolByName(portal, 'portal_setup'))

    def add_criterion(self, index, criterion, value=None):
        portal = self.layer['portal']
        name = '%s_%s' % (index, criterion)
        portal.topic.addCriterion(index, criterion)
        crit = portal.topic.getCriterion(name)
        if value is not None:
            crit.setValue(value)
        return crit

    def test_migrate_simple_topic(self):
        portal = self.layer['portal']
        self.assertEqual(portal.topic.portal_type, 'Topic')
        self.assertEqual(portal.topic.getLayout(), 'atct_topic_view')
        self.assertEqual(portal.topic.getAcquireCriteria(), False)
        self.assertEqual(portal.topic.getLimitNumber(), False)
        self.assertEqual(portal.topic.getItemCount(), 0)
        self.assertEqual(portal.topic.getCustomViewFields(), ('Title',))
        self.run_migration()
        self.assertEqual(portal.topic.portal_type, 'Collection')
        self.assertEqual(portal.topic.getLayout(), 'standard_view')
        self.assertEqual(portal.topic.getAcquireCriteria(), False)
        self.assertEqual(portal.topic.getSort_on(), 'sortable_title')
        self.assertEqual(portal.topic.getSort_reversed(), False)
        self.assertEqual(portal.topic.getLimit(), 1000)
        self.assertEqual(portal.topic.getCustomViewFields(), ('Title',))

    def test_migrate_topic_fields(self):
        portal = self.layer['portal']
        portal.topic.setAcquireCriteria(True)
        portal.topic.setText('<p>Hello</p>')
        portal.topic.setLimitNumber(True)
        portal.topic.setItemCount(42)
        portal.topic.setCustomViewFields(('Title', 'Type'))
        self.run_migration()
        self.assertEqual(portal.topic.portal_type, 'Collection')
        self.assertEqual(portal.topic.getAcquireCriteria(), True)
        self.assertEqual(portal.topic.getLimit(), 42)
        self.assertEqual(portal.topic.getCustomViewFields(),
                         ('Title', 'Type'))

    def test_migrate_layout(self):
        portal = self.layer['portal']
        portal.topic.setAcquireCriteria(True)
        portal.topic.setLayout('folder_summary_view')
        self.run_migration()
        self.assertEqual(portal.topic.getLayout(), 'summary_view')

    def test_migrate_customView(self):
        portal = self.layer['portal']
        portal.topic.setAcquireCriteria(True)
        portal.topic.setCustomView(True)
        self.run_migration()
        self.assertEqual(portal.topic.getLayout(), 'tabular_view')

    def test_migrate_nested_topic(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.portal_types.Topic.filter_content_types = False
        portal.portal_types.Collection.filter_content_types = False
        portal.topic.invokeFactory("Topic", "subtopic", title="Sub Topic")
        self.run_migration()
        self.assertEqual(portal.topic.portal_type, 'Collection')
        self.assertEqual(portal.topic.subtopic.portal_type, 'Collection')

    def test_ATSimpleStringCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('SearchableText', 'ATSimpleStringCriterion', 'bar')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'SearchableText',
                           'o': 'plone.app.querystring.operation.string.contains',
                           'v': 'bar'}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATDateCriteriaPast(self):
        portal = self.layer['portal']
        # More than 5 days in the past:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('more')
        crit.setDateRange('-')
        # Less than 5 days in the past:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('less')
        crit.setDateRange('-')
        # The next two are logically a bit weird.
        # More than 0 days in the past is historically interpreted as: after today.
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('more')
        crit.setDateRange('-')
        # Less than 0 days in the past is historically interpreted as: before today.
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('less')
        crit.setDateRange('-')

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.largerThanRelativeDate')
        self.assertEqual(query[0]['v'], -5)

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.lessThanRelativeDate')
        self.assertEqual(query[1]['v'], -5)

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(query[2]['o'], 'plone.app.querystring.operation.date.afterToday')
        self.assertTrue('v' not in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(query[3]['o'], 'plone.app.querystring.operation.date.beforeToday')
        self.assertTrue('v' not in query[3].keys())

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATDateCriteriaFuture(self):
        portal = self.layer['portal']
        # More than 5 days in the future:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('more')
        crit.setDateRange('+')
        # Less than 5 days in the future:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('less')
        crit.setDateRange('+')
        # More than 0 days in the future: after today.
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('more')
        crit.setDateRange('+')
        # Less than 0 days in the future: before today.
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('less')
        crit.setDateRange('+')

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.largerThanRelativeDate')
        self.assertEqual(query[0]['v'], 5)

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.lessThanRelativeDate')
        self.assertTrue(query[1]['v'], 5)

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(query[2]['o'], 'plone.app.querystring.operation.date.afterToday')
        self.assertTrue('v' not in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(query[3]['o'], 'plone.app.querystring.operation.date.beforeToday')
        self.assertTrue('v' not in query[3].keys())

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATDateCriteriaExactDay(self):
        portal = self.layer['portal']
        #time1 = DateTime()
        # 5 days ago:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('within_day')
        crit.setDateRange('-')
        # 5 days from now:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('within_day')
        crit.setDateRange('+')
        # past or future does not matter if the day is today.
        # today minus
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('within_day')
        crit.setDateRange('-')
        # today plus
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('within_day')
        crit.setDateRange('+')

        self.run_migration()
        query = portal.topic.getRawQuery()
        time2 = DateTime()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.between')
        self.assertEqual(query[0]['v'], ((time2 - 5).earliestTime(), (time2 - 5).latestTime()))

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.between')
        self.assertEqual(query[1]['v'], ((time2 + 5).earliestTime(), (time2 + 5).latestTime()))

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(query[2]['o'], 'plone.app.querystring.operation.date.today')
        self.assertFalse('v' in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(query[3]['o'], 'plone.app.querystring.operation.date.today')
        self.assertFalse('v' in query[3].keys())

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATCurrentAuthorCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('Creator', 'ATCurrentAuthorCriterion')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'Creator',
                           'o': 'plone.app.querystring.operation.string.currentUser',
                           'v': 'admin'}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATListCriterion(self):
        portal = self.layer['portal']
        # The new-style queries do not currently offer the possibility
        # to choose if the given values should be joined with 'or' or
        # 'and'.  Default is 'or'.
        crit = self.add_criterion('Subject', 'ATListCriterion', ('foo', 'bar'))
        crit.setOperator('or')
        # Note: this could have been an ATPortalTypeCriterion too:
        crit = self.add_criterion('portal_type', 'ATListCriterion', ('Document', 'Folder'))
        crit.setOperator('and')

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'Subject',
                          'o': 'plone.app.querystring.operation.selection.is',
                          'v': ('foo', 'bar')})
        self.assertEqual(query[1],
                         {'i': 'portal_type',
                          'o': 'plone.app.querystring.operation.selection.is',
                          'v': ('Document', 'Folder')})

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATPathCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('path', 'ATPathCriterion', portal.folder.UID())
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': portal.folder.UID()}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATPathCriterionNonRecursive(self):
        # Topics supported non recursive search, so search at a specific
        # depth.  New Collections do not support it.
        portal = self.layer['portal']
        crit = self.add_criterion('path', 'ATPathCriterion', portal.folder.UID())
        crit.setRecurse(True)
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': portal.folder.UID()}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATPathCriterionDouble(self):
        # Collections currently support only one path.
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Folder", "folder2", title="Folder 2")
        self.add_criterion('path', 'ATPathCriterion', [portal.folder.UID(), portal.folder2.UID()])
        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 1)
        self.assertEqual(query[0]['i'], 'path')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.string.path')
        # Which of the paths is taken is not defined.  This might
        # depend on the sort order of the uids.
        self.assertTrue(query[0]['v'] in (portal.folder.UID(), portal.folder2.UID()))

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATBooleanCriterion(self):
        # Note that in standard Plone the boolean criterion is only
        # defined for is_folderish and is_default_page.
        portal = self.layer['portal']
        crit = self.add_criterion('is_folderish', 'ATBooleanCriterion')
        crit.setBool(True)
        crit = self.add_criterion('is_default_page', 'ATBooleanCriterion')
        crit.setBool(False)

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'is_folderish',
                          'o': 'plone.app.querystring.operation.boolean.isTrue'})
        self.assertEqual(query[1],
                         {'i': 'is_default_page',
                          'o': 'plone.app.querystring.operation.boolean.isFalse'})

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATDateRangeCriteria(self):
        portal = self.layer['portal']
        time1 = DateTime()
        # Days in the past:
        crit = self.add_criterion('created', 'ATDateRangeCriterion')
        crit.setStart(time1 - 5)
        crit.setEnd(time1 - 3)
        # Past and future:
        crit = self.add_criterion('effective', 'ATDateRangeCriterion')
        crit.setStart(time1 - 2)
        crit.setEnd(time1 + 2)
        # Days in the future:
        crit = self.add_criterion('expires', 'ATDateRangeCriterion')
        crit.setStart(time1 + 3)
        crit.setEnd(time1 + 5)

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 3)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.between')
        self.assertEqual(query[0]['v'], (time1 - 5, time1 - 3))

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.between')
        self.assertEqual(query[1]['v'], (time1 - 2, time1 + 2))

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(query[2]['o'], 'plone.app.querystring.operation.date.between')
        self.assertEqual(query[2]['v'], (time1 + 3, time1 + 5))

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATPortalTypeCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('portal_type', 'ATPortalTypeCriterion', ('Document', 'Folder'))
        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(query,
                         [{'i': 'portal_type',
                           'o': 'plone.app.querystring.operation.selection.is',
                           'v': ('Document', 'Folder')}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATPortalTypeCriterionOfTopic(self):
        portal = self.layer['portal']
        # We migrate Topics to Collections, so we should update
        # criterions that search for Topics.
        self.add_criterion('portal_type', 'ATPortalTypeCriterion', ('Topic',))
        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(query,
                         [{'i': 'portal_type',
                           'o': 'plone.app.querystring.operation.selection.is',
                           'v': ('Collection',)}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSelectionCriterion(self):
        portal = self.layer['portal']
        # The new-style queries do not currently offer the possibility
        # to choose if the given values should be joined with 'or' or
        # 'and'.  Default is 'or'.
        crit = self.add_criterion('Subject', 'ATSelectionCriterion', ('foo', 'bar'))
        crit.setOperator('or')
        # Note: this could have been an ATPortalTypeCriterion too:
        # Note that we check that Topic is turned into Collection too.
        crit = self.add_criterion('portal_type', 'ATSelectionCriterion', ('Document', 'Topic'))
        crit.setOperator('and')

        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'Subject',
                          'o': 'plone.app.querystring.operation.selection.is',
                          'v': ('foo', 'bar')})
        self.assertEqual(query[1],
                         {'i': 'portal_type',
                          'o': 'plone.app.querystring.operation.selection.is',
                          'v': ('Document', 'Collection')})

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATReferenceCriterion(self):
        # Note: the new criterion is disabled by default.  Also, it
        # needs the _referenceIs function in the plone.app.querystring
        # queryparser and that function is not defined.
        portal = self.layer['portal']
        self.add_criterion('getRawRelatedItems', 'ATReferenceCriterion', portal.folder.UID())
        self.run_migration()
        # TODO re-enable this check when the queryparser works.
        # self.assertEqual(portal.topic.getRawQuery(),
        #                  [{'i': 'getRawRelatedItems',
        #                    'o': 'plone.app.querystring.operation.reference.is',
        #                    'v': (portal.folder.UID(),)}])

        # Check that the resulting query does not give an error.
        #portal.topic.getQuery()

    def test_ATRelativePathCriterion(self):
        portal = self.layer['portal']
        crit = self.add_criterion('path', 'ATRelativePathCriterion')
        crit.setRelativePath('../folder')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.relativePath',
                           'v': '../folder'}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATRelativePathCriterionNonRecursive(self):
        # Topics supported non recursive search, so search at a specific
        # depth.  New Collections do not support it.
        portal = self.layer['portal']
        crit = self.add_criterion('path', 'ATRelativePathCriterion')
        crit.setRelativePath('../folder')
        crit.setRecurse(True)
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.relativePath',
                           'v': '../folder'}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSimpleIntCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('getObjPositionInParent', 'ATSimpleIntCriterion', 7)
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'getObjPositionInParent',
                           'o': 'plone.app.querystring.operation.int.is',
                           'v': 7}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSimpleIntCriterionMinimum(self):
        portal = self.layer['portal']
        crit = self.add_criterion('getObjPositionInParent', 'ATSimpleIntCriterion', 6)
        crit.setDirection('min')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'getObjPositionInParent',
                           'o': 'plone.app.querystring.operation.int.largerThan',
                           'v': 6}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSimpleIntCriterionMaximum(self):
        portal = self.layer['portal']
        crit = self.add_criterion('getObjPositionInParent', 'ATSimpleIntCriterion', 5)
        crit.setDirection('max')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'getObjPositionInParent',
                           'o': 'plone.app.querystring.operation.int.lessThan',
                           'v': 5}])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSimpleIntCriterionBetween(self):
        # This is not supported.
        portal = self.layer['portal']
        crit = self.add_criterion('getObjPositionInParent', 'ATSimpleIntCriterion', 4)
        crit.setDirection('min:max')
        crit.setValue2(8)
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(), [])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSortCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('modified', 'ATSortCriterion')
        self.run_migration()
        self.assertEqual(portal.topic.getSort_on(), 'modified')
        self.assertEqual(portal.topic.getSort_reversed(), False)
        self.assertEqual(portal.topic.getRawQuery(), [])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()

    def test_ATSortCriterionReversed(self):
        portal = self.layer['portal']
        crit = self.add_criterion('created', 'ATSortCriterion')
        crit.setReversed(True)
        self.run_migration()
        self.assertEqual(portal.topic.getSort_on(), 'created')
        self.assertEqual(portal.topic.getSort_reversed(), True)
        self.assertEqual(portal.topic.getRawQuery(), [])

        # Check that the resulting query does not give an error.
        portal.topic.getQuery()
