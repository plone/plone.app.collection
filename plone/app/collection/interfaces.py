from zope.interface import Interface
from plone.registry import field

class ICollection(Interface):
    """ """
    pass

class ICollectionOperation(Interface):
    title = field.TextLine(title=u"Title")
    description = field.Text(title=u"Description")
    operator = field.TextLine(title=u"Operator")
    widget = field.TextLine(title=u"widget")

class ICollectionField(Interface):
    title = field.TextLine(title=u"Title")
    description = field.Text(title=u"Description")
    enabled = field.Bool(title=u"Enabled")
    operations = field.List(title=u"Operations")
    vocabulary = field.TextLine(title=u"Vocabulary")
