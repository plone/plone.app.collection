import os
import unittest

from plone.testing import layered

from plone.app.collection.testing import PLONEAPPCOLLECTION_ACCEPTANCE_TESTING

import robotsuite


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.txt') and doc.startswith('robot_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(
                robotsuite.RobotTestSuite(test),
                layer=PLONEAPPCOLLECTION_ACCEPTANCE_TESTING
            ),
        ])
    return suite
