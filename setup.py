from setuptools import setup, find_packages

version = '1.0.2'

setup(name='plone.app.collection',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],
      keywords='',
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
          'archetypes.querywidget',
          'plone.app.contentlisting',
          'plone.app.form',
          'plone.app.portlets',
          'plone.app.testing',
          'plone.app.vocabularies',
          'plone.portlets',
          'plone.testing',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.CMFQuickInstallerTool',
          'Products.validation',
          'transaction',
          'unittest2',
          'zope.component',
          'zope.configuration',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'Zope2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
