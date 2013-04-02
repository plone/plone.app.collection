from Acquisition import aq_inner
from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.foldercontents import FolderContentsBrowserView


class SubCollectionsView(FolderContentsView):

    def contents_table(self):
        table = SubCollectionsTable(aq_inner(self.context), self.request)
        return table.render()


class SubCollectionsTable(FolderContentsTable):

    def contentsMethod(self):
        # Explicitly do *not* use the queryCatalog method.
        context = aq_inner(self.context)
        return context.getFolderContents


class SubCollectionsBrowserView(FolderContentsBrowserView):
    table = SubCollectionsTable
