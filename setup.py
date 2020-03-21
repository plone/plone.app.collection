# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.2.8'

setup(name='plone.app.collection',
      version=version,
      description="This package adds 'saved search' functionality to Plone.",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Development Status :: 6 - Mature",
          "Framework :: Plone",
          "Framework :: Plone :: 5.1",
          "Framework :: Plone :: 5.2",
          "Framework :: Plone :: Core",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='plone collection topic smartfolder saved search',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/plone.app.collection',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.contentlisting',
          'plone.app.portlets',
          'plone.app.querystring>=1.2.2',  # custom_query support
          'plone.app.vocabularies',
          'plone.app.widgets',
          'plone.portlet.collection',
          'plone.portlets',
          'Products.Archetypes>=1.10.4.dev0',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.validation',
          'transaction',
          'zope.component',
          'zope.configuration',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'Zope2',
      ],
      extras_require={
          'test': [
              'plone.app.testing [robot]',
              'Products.ATContentTypes [test]',
              ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
