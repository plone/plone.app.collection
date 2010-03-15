from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from interfaces import IPACollectionSettings
#from plone.z3cform import layout
from zope.i18nmessageid import MessageFactory
#from Products.CMFPlone.utils import log

_ = MessageFactory('plone.app.collection')


class PACollectionControlPanelForm(RegistryEditForm):
    schema = IPACollectionSettings
    label = _(u"Collections settings")
    description = _(u"Please enter the settings.")


class PACollectionControlPanelFormView(ControlPanelFormWrapper):
    form = PACollectionControlPanelForm
