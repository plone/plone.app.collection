from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.add import DefaultAddForm

from plone.dexterity.browser.edit import DefaultEditView
from plone.dexterity.browser.edit import DefaultEditForm

from plone.formwidget.querystring.widget import QueryStringFieldWidget


class CollectionAddForm(DefaultAddForm):

    def updateFields(self):
        super(CollectionAddForm, self).updateFields()
        self.fields['query'].widgetFactory = QueryStringFieldWidget


class CollectionAddView(DefaultAddView):

    form = CollectionAddForm


class CollectionEditForm(DefaultEditForm):

    def updateFields(self):
        super(CollectionEditForm, self).updateFields()
        self.fields['query'].widgetFactory = QueryStringFieldWidget

class CollectionEditView(DefaultEditView):

    form = CollectionEditForm
