import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
#    read('plone', 'app', 'collection', 'README.txt')
#    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

tests_require = ['collective.testcaselayer']

setup(name='plone.app.collection',
      version=version,
      description="",
      long_description=long_description,
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
          'archetypes.querywidget',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
