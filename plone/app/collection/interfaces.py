from zope.interface import Interface
from zope.schema import TextLine, Text, Bool, List, DottedName

class ICollection(Interface):
    """ """
    pass

class ICollectionRegistryReader(Interface):
    """Marker interface for the registry adapter"""

class IQueryOperation(Interface):
    title = TextLine(title=u"Title")
    description = Text(title=u"Description")
    operation = TextLine(title=u"Operation")
    widget = TextLine(title=u"Widget")

class IQueryField(Interface):
    title = TextLine(title=u"Title")
    description = Text(title=u"Description")
    enabled = Bool(title=u"Enabled")
    sortable = Bool(title=u"Sortable")
    operations = List(title=u"Operations", value_type=DottedName(title=u"Operation ID"))
    vocabulary = TextLine(title=u"Vocabulary")
    group = TextLine(title=u"Group")
