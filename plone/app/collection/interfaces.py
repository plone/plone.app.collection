from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides

from plone.autoform import directives as form

from plone.autoform.interfaces import IFormFieldProvider
from plone.formwidget.querystring.widget import QueryStringFieldWidget

from plone.supermodel import model

from plone.app.collection import _


class IPloneAppCollectionLayer(Interface):
    """Marker interface for the plone.app.collection browser layer.
    """

class ICollection(Interface):
    """
    """


class ICollectionBehavior(model.Schema):

    form.widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u'label_query', default=u'Search terms'),
        description=_(u"""Define the search terms for the items you want to
            list by choosing what to match on.
            The list of results will be dynamically updated"""),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False
    )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
        default=False,
    )

    limit = schema.Int(
        title=_(u'label_limit', default=u'limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
    )

    #customViewFields = schema.Choice(
    #    title=_(u'label_sort_on', default=u'sortable_title'),
    #    description=_(u"Sort the collection on this index"),
    #    required=False,
    #    )

    #form.order_before(title='*')
    #form.order_after(description='title')

    def listMetaDataFields(exclude=True):
        """Return a list of all metadata fields from portal_catalog.
        """

    def results(batch=True, b_start=0, b_size=None):
        """
        """

    def selectedViewFields():
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """

    def getFoldersAndImages():
        """
        """


alsoProvides(ICollectionBehavior, IFormFieldProvider)
