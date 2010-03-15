#from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from plone.directives import form

_ = MessageFactory('plone.app.collection')


class IPACollectionSettings(form.Schema):
    """This interface defines the plone.app.collection settings."""
