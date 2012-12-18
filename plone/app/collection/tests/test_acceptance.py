import os
import unittest

from plone.testing import layered

from plone.app.collection.testing import PLONEAPPCOLLECTION_ACCEPTANCE_TESTING

import robotsuite


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    acceptance_dir = os.path.join(current_dir, 'acceptance')
    acceptance_tests = [os.path.join('acceptance', doc) for doc in
                        os.listdir(acceptance_dir) if doc.endswith('.txt') and
                        doc.startswith('test_')]
    for test in acceptance_tests:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(test),
            layer=PLONEAPPCOLLECTION_ACCEPTANCE_TESTING),
        ])
    return suite


#def test_suite():
#    suite = unittest.TestSuite()
#    suite.addTests([
#        layered(robotsuite.RobotTestSuite("acceptance/test_collection.txt"),
#        layer=PLONEAPPCOLLECTION_ACCEPTANCE_TESTING),
#    ])
#    return suite

#def test_suite():
#    suite = unittest.TestSuite()
#    suite.addTests([
#        layered(robotsuite.RobotTestSuite("acceptance/test_collection.txt"),
#        layer=PLONEAPPCOLLECTION_ACCEPTANCE_TESTING),
#    ])
#    return suite
