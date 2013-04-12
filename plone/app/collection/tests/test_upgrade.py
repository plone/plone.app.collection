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
        self.run_migration()
        self.assertEqual(portal.topic.portal_type, 'Collection')

    def test_ATSimpleStringCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('SearchableText', 'ATSimpleStringCriterion', 'bar')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'SearchableText',
                           'o': 'plone.app.querystring.operation.string.contains',
                           'v': 'bar'}])

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

    def test_ATCurrentAuthorCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('Creator', 'ATCurrentAuthorCriterion')
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'Creator',
                           'o': 'plone.app.querystring.operation.string.currentUser',
                           'v': 'admin'}])

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

    def test_ATPathCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('path', 'ATPathCriterion', portal.folder.UID())
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': '/plone/folder'}])

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
                           'v': '/plone/folder'}])

    def test_ATPathCriterionDouble(self):
        # Collections currently support only one path.
        portal = self.layer['portal']
        login(portal, 'admin')
        portal.invokeFactory("Folder", "folder2", title="Folder 2")
        self.add_criterion('path', 'ATPathCriterion', [portal.folder.UID(), portal.folder2.UID()])
        self.run_migration()
        self.assertEqual(portal.topic.getRawQuery(),
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': '/plone/folder'}])

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

    def test_ATPortalTypeCriterion(self):
        portal = self.layer['portal']
        self.add_criterion('portal_type', 'ATPortalTypeCriterion', ('Document', 'Folder'))
        self.run_migration()
        query = portal.topic.getRawQuery()
        self.assertEqual(query,
                         [{'i': 'portal_type',
                           'o': 'plone.app.querystring.operation.selection.is',
                           'v': ('Document', 'Folder')}])
