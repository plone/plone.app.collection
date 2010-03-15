from zope.interface import Interface
from plone.registry import field

class ICollection(Interface):
    """ """
    pass

class IQueryOperation(Interface):
    title = field.TextLine(title=u"Title")
    description = field.Text(title=u"Description")
    operation = field.TextLine(title=u"Operation")
    widget = field.TextLine(title=u"widget")

class IQueryField(Interface):
    title = field.TextLine(title=u"Title")
    description = field.Text(title=u"Description")
    enabled = field.Bool(title=u"Enabled")
    operations = field.List(title=u"Operations")
    vocabulary = field.TextLine(title=u"Vocabulary")
