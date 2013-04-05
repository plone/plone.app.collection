from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login

from .base import CollectionMigrationTestCase
from plone.app.collection.upgrade import migrate_topics

# default test query
query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class TestCriterionConverters(CollectionMigrationTestCase):

    def run_migration(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        migrate_topics(getToolByName(portal, 'portal_setup'))

    def add_criterion(self, index, criterion, value, operation=None,
                      date_range=None):
        portal = self.layer['portal']
        name = '%s_%s' % (index, criterion)
        portal.topic.addCriterion(index, criterion)
        crit = portal.topic.getCriterion(name)
        crit.setValue(value)
        if operation is not None:
            crit.setOperation(operation)
        if date_range is not None:
            crit.setDateRange(date_range)

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
        time1 = DateTime()
        # More than 5 days in the past:
        self.add_criterion('created', 'ATFriendlyDateCriteria', 5, operation='more', date_range='-')
        # Less than 5 days in the past:
        self.add_criterion('effective', 'ATFriendlyDateCriteria', 5, operation='less', date_range='-')
        # The next two are logically a bit weird.
        # More than 0 days in the past is historically interpreted as: after today.
        self.add_criterion('expires', 'ATFriendlyDateCriteria', 0, operation='more', date_range='-')
        # Less than 0 days in the past is historically interpreted as: before today.
        self.add_criterion('modified', 'ATFriendlyDateCriteria', 0, operation='less', date_range='-')
        self.run_migration()
        query = portal.topic.getRawQuery()
        time2 = DateTime()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.lessThan')
        self.assertEqual(query[0]['v'], (time1 - 5).earliestTime())

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.between')
        self.assertTrue(query[1]['v'], time2)

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(query[2]['o'], 'plone.app.querystring.operation.date.afterToday')
        self.assertTrue('v' not in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(query[3]['o'], 'plone.app.querystring.operation.date.beforeToday')
        self.assertTrue('v' not in query[3].keys())

    def test_ATDateCriteriaFuture(self):
        portal = self.layer['portal']
        time1 = DateTime()
        # More than 5 days in the future:
        self.add_criterion('created', 'ATFriendlyDateCriteria', 5, operation='more', date_range='+')
        # Less than 5 days in the future:
        self.add_criterion('effective', 'ATFriendlyDateCriteria', 5, operation='less', date_range='+')
        # More than 0 days in the future: after today.
        self.add_criterion('expires', 'ATFriendlyDateCriteria', 0, operation='more', date_range='+')
        # Less than 0 days in the future: before today.
        self.add_criterion('modified', 'ATFriendlyDateCriteria', 0, operation='less', date_range='+')
        self.run_migration()
        query = portal.topic.getRawQuery()
        time2 = DateTime()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(query[0]['o'], 'plone.app.querystring.operation.date.largerThan')
        self.assertEqual(query[0]['v'], (time1 + 5).earliestTime())

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(query[1]['o'], 'plone.app.querystring.operation.date.between')
        self.assertTrue(query[1]['v'], time2)

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
        self.add_criterion('created', 'ATFriendlyDateCriteria', 5, operation='within_day', date_range='-')
        # 5 days from now:
        self.add_criterion('effective', 'ATFriendlyDateCriteria', 5, operation='within_day', date_range='+')
        # past or future does not matter if the day is today.
        # today minus
        self.add_criterion('expires', 'ATFriendlyDateCriteria', 0, operation='within_day', date_range='-')
        # today plus
        self.add_criterion('modified', 'ATFriendlyDateCriteria', 0, operation='within_day', date_range='+')
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
