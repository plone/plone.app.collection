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
  
  [ ] Make sure the edit view is fully functional.
  
  [ ] Re-create class/view methods of the old collection type.
  
  [ ] Make the standard collection views work.
  
  [ ] Make enableSyndication/RSS work. Syndication is not working for 
      plone.app.collection trunk either.

  [ ] Make the collection portlet work.



Problems::

  - plone.app.querystring results.pt "LocationError: ([], 'actual_result_count')"::
  - Fix: comment out section::
    
    <!--<span i18n:translate="batch_x_items_matching_your_criteria">
        <strong i18n:name="number" id="search-results-number"
                tal:content="results/actual_result_count">234</strong>
        items matching your search terms.
    </span>-->
    
