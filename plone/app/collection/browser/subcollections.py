from Acquisition import aq_inner, aq_parent
from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
try:
    from plone.app.content.browser.foldercontents import \
        FolderContentsBrowserView
    FolderContentsBrowserView  # pyflakes
except ImportError:
    # BBB for Plone 4.2 (plone.app.content 2.0)
    from plone.app.content.browser.foldercontents import \
        FolderContentsKSSView as FolderContentsBrowserView


class SubCollectionsView(FolderContentsView):

    def contents_table(self):
        table = SubCollectionsTable(aq_inner(self.context), self.request)
        return table.render()

    def renderBase(self):
        """Returns the URL used in the base tag.

        BBB for Plone 4.2 (plone.app.content 2.0).  Later versions of
        plone.app.content define their own renderBase already.
        """
        # Assume a folderish context
        return self.context.absolute_url() + '/'

    def has_parent_collection(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        if not hasattr(parent, 'portal_type'):
            return False
        return parent.portal_type == context.portal_type

    def add_url(self):
        return '%s/createObject?type_name=%s' % (
            self.renderBase(), self.context.portal_type)


class SubCollectionsTable(FolderContentsTable):

    def contentsMethod(self):
        # Explicitly do *not* use the queryCatalog method.
        context = aq_inner(self.context)
        return context.getFolderContents


class SubCollectionsBrowserView(FolderContentsBrowserView):
    table = SubCollectionsTable
