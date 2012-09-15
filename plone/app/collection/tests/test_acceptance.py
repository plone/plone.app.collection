import unittest

from plone.testing import layered

from plone.app.collection.testing import PLONEAPPCOLLECTION_ACCEPTANCE_TESTING

import robotsuite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("acceptance/test_collection.txt"),
        layer=PLONEAPPCOLLECTION_ACCEPTANCE_TESTING),
    ])
    return suite
