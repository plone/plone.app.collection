from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plone.app.collection',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.contentlisting',
          'plone.app.vocabularies',
          'collective.testcaselayer',
          'plone.directives.form',
          'archetypes.querywidget',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
