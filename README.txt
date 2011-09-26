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


Todo::

  [X] Create basic dexterity-based collection type.

  [X] Use QueryStringWidget (plone.formwidget.querystring) for the query field.

  [X] Make sure the edit view is fully functional.

  [X] Re-create class/view methods of the old collection type.

  [X] Make the standard collection views work.

  [X] Make enableSyndication/RSS work. Syndication is not working for 
      plone.app.collection trunk either.

  [ ] Make the tabular_view and the in-out-widget for the customViewFields field work.

  [ ] Make the collection portlet work.
