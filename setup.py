# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.0.16.dev0'

setup(name='plone.app.collection',
      version=version,
      description="This package adds 'saved search' functionality to Plone.",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='plone collection topic smartfolder saved search',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.collection',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.querywidget>=1.1.1.dev0',  # custom_query support
          'plone.app.contentlisting',
          'plone.app.form',
          'plone.app.portlets',
          'plone.app.vocabularies',
          'plone.portlet.collection',
          'plone.portlets',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.CMFQuickInstallerTool',
          'Products.validation',
          'transaction',
          'zope.component',
          'zope.configuration',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'Zope2',
      ],
      extras_require={
          'test': [
              'plone.app.robotframework',
              ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
