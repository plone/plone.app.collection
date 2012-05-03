from setuptools import setup, find_packages
import os

version = '2.0b2dev'

setup(name='plone.app.collection',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Timo Stollenwerk - Plone Foundation',
      author_email='contact@timostollenwerk.net',
      url='http://github.com/plone/plone.app.collection',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.contentmenu',
          'plone.formwidget.querystring',
      ],
      extras_require={
          'test': [
              'lxml',
              'plone.app.testing',
           ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
