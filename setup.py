from setuptools import setup, find_packages

version = '1.0.8.dev0'

setup(name='plone.app.collection',
      version=version,
      description="This package adds 'saved search' functionality to Plone.",
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
          'archetypes.querywidget>=1.0.2dev',
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
              'plone.app.testing [robot]',
              ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
