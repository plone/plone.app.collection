from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope import schema

from plone.app.collection import PloneMessageFactory as _


class ICollectionPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    target_collection = schema.Choice(
        title=_(u"Target collection"),
        description=_(u"Find the collection which provides the items to "
            "list"),
        required=True,
        source=SearchableTextSourceBinder({'portal_type': 'Collection'},
            default_query='path:'))

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Specify the maximum number of items to show in the "
            "portlet."),
        required=False,
        default=10)

    show_more = schema.Bool(
        title=_(u"Show more... link"),
        description=_(u"If enabled, a more... link will appear in the "
            "footer of the portlet, linking to the underlying Collection."),
        required=True,
        default=True)

    show_dates = schema.Bool(
        title=_(u"Show dates"),
        description=_(u"If enabled, effective dates will be shown "
            "underneath the items listed."),
        required=True,
        default=False)


class Assignment(base.Assignment):

    implements(ICollectionPortlet)

    header = u""
    target_collection = None
    limit = 10
    show_more = True
    show_dates = False

    def __init__(self, header=u"",
                 target_collection=None,
                 limit=10,
                 show_more=True,
                 show_dates=False):
        self.header = header
        self.target_collection = target_collection
        self.limit = limit
        self.show_more = show_more
        self.show_dates = show_dates

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/collectionportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    render = _template

    @property
    def available(self):
        return len(self.results()) > 0

    def collection_url(self):
        collection = self.collection()
        if collection:
            return collection.absolute_url()

    def results(self):
        """ Get the actual result brains from the collection.
            This is a wrapper so that we can memoize if and only if we aren't
            selecting random items."""
        return self._standard_results()

    def _standard_results(self):
        collection = self.collection()
        if not collection:
            return []
        return collection.getQuery(batch=False, limit=self.data.limit)

    def collection(self):
        """Get the collection the portlet is pointing to"""
        collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]

        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(collection_path, unicode):
            # restrictedTraverse accept only strings
            collection_path = str(collection_path)
        return portal.restrictedTraverse(collection_path, default=None)


class AddForm(base.AddForm):

    form_fields = form.Fields(ICollectionPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Add Collection Portlet")
    description = _(u"This portlet display a listing of items from a "
        "Collection.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    form_fields = form.Fields(ICollectionPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Edit Collection Portlet")
    description = _(u"This portlet display a listing of items from a "
        "Collection.")
