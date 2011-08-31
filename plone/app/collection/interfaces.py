from zope import schema
from zope import interface

from plone.directives import form

from plone.formwidget.querystring.widget import QueryStringFieldWidget

from plone.app.collection import _


class IPloneAppCollectionLayer(interface.Interface):
    """Marker interface for the plone.app.collection browser layer.
    """


class ICollection(form.Schema):

    form.widget(query=QueryStringFieldWidget)
    query = schema.TextLine(
        title=_(u'label_query', default=u'Search terms'),
        description=_(u"""Define the search terms for the items you want to
            list by choosing what to match on.
            The list of results will be dynamically updated"""),
        required=False,
        )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'sortable_title'),
        description=_(u"Sort the collection on this index"),
        required=False,
        )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'sort_reversed'),
        description=_(u'Sort the results in reversed order'),
        required=False,
        )

    limit = schema.Int(
        title=_(u'label_limit', default=u'limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
        )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'sortable_title'),
        description=_(u"Sort the collection on this index"),
        required=False,
        )

    #customViewFields = schema.Choice(
    #    title=_(u'label_sort_on', default=u'sortable_title'),
    #    description=_(u"Sort the collection on this index"),
    #    required=False,
    #    )

    #form.order_before(title='*')
    #form.order_after(description='title')

