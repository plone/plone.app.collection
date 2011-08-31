Introduction
============

Experimental dexterity-based plone.app.collection.

You can try it out by running the buildout inside this package.

Instead of the archetypes.querywidget AT-widget plone.app.collection relies
on plone.formwidget.querystring, which is a z3c.form implementation of
archetypes.querywidget.

This branch of plone.app.collection requires a branch of 
plone.formwidget.querystring::

http://svn.plone.org/svn/plone/plone.formwidget.querystring/branches/tisto/

Current status::

  - The basic dexterity-based collection type is in place.
  - Class methods of the old collection type are still missing.
  - The edit view of the collection is basically working. Some functionality
    might be broken though.
  - The collection views are currently not working at all.
