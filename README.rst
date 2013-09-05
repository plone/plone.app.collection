Introduction
============

WARNING!!!

This is the Dexterity-based branch of plone.app.collection which will not be
developed further. The code has been merged into plone.app.contententtypes!

There is a good chance you don't want to make any changes here! If you want to
add enhancements please do it in plone.app.contenttypes.

WARNING!!!

Collections in Plone are the most powerful tool content editors and site
managers have to construct navigation and site sections.

This is a brand new implementation of collections for Plone, using
ajax/javascript to make a simpler, easier and streamlined user experience
for using collections. Having a more lightweight backend that does not depend
on many nested criteria types.

It's designed with simplicity and usability as a main focus, so content editors
and site managers can create complex search queries with ease.

.. note::

  This is the dexterity-based version of plone.app.collection. If you are
  looking for the ATContentTypes-based version that is included in Plone
  since version 4.2, stay with the 1.x branch of plone.app.collection.


How to add your own criteria to a collection
--------------------------------------------

plone.app.collection and (or more precisely the underlying
plone.app.querystring) uses plone.app.registry records to define possible
search criteria for a collection.

If you want to add your own criteria, say to choose a value from a custom
index, you have to create a plone.app.registry record for this index in your
generic setup profile (e.g profiles/default/registry.xml)::

    <registry>
      <records interface="plone.app.querystring.interfaces.IQueryField"
               prefix="plone.app.querystring.field.department">
        <value key="title">Department</value>
        <value key="description">A custom department index</value>
        <value key="enabled">True</value>
        <value key="sortable">False</value>
        <value key="operations">
            <element>plone.app.querystring.operation.string.is</element>
        </value>
        <value key="group">Metadata</value>
      </records>
    </registry>

The title-value refers to the custom index ("Department"), the operations-value
is used to filter the items and the group-value defines under which group the
entry shows up in the selection widget.

.. note::

    For a full list of all existing QueryField declarations see
    https://github.com/plone/plone.app.querystring/blob/master/plone/app/querystring/profiles/default/registry.xml#L164

    For a full list of all existing operations see
    https://github.com/plone/plone.app.querystring/blob/master/plone/app/querystring/profiles/default/registry.xml#L1
