from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility, adapts
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from interfaces import ICollectionRegistryReader
#from Products.CMFCore.utils import getToolByName


class DottedDict(dict):
    """A dictionary where you can access nested dicts with dotted names"""

    def get(self, k, default=None):
        if not '.' in k:
            return super(DottedDict, self).get(k, default)
        val = self
        for x in k.split('.'):
            val = val[x]
        return val


class CollectionRegistryReader(object):
    """Adapts a registry object to parse the collection data"""

    implements(ICollectionRegistryReader)
    adapts(IRegistry)
    prefix = "plone.app.collection"

    def __init__(self, context):
        self.context = context

    def parseRegistry(self):
        """Make a dictionary structure for the values in the registry"""
        result = DottedDict()
        for record in self.context.records:
            splitted = record.split('.')
            current = result
            for x in splitted[:-1]:
                # create the key if it's not there
                if not x in current:
                    current[x] = {}
                current = current[x]

            # store actual key/value
            key = splitted[-1]
            current[key] = self.context.records[record].value

        return result

    def getVocabularyValues(self, values):
        """Get all vocabulary values if a vocabulary is defined"""
        for field in values.get(self.prefix + '.field').values():
            vocabulary = field.get('vocabulary', [])
            if vocabulary:
                utility = getUtility(IVocabularyFactory, vocabulary)
                field['values'] = {}
                for item in utility(self.context):
                    field['values'][item.value] = \
                        {'friendly_name': item.title}
        return values

    def mapOperations(self, values):
        """Get the operations from the registry and put them in the key
           'operators' with the short name as key
        """
        for field in values.get(self.prefix + '.field').values():
            fieldoperations = field.get('operations', [])
            for operation_key in fieldoperations:
                try:
                    field['operators'][operation_key.split('.')[-1]] = \
                        values.get(operation_key)
                except KeyError:
                    # invalid operation, probably doesn't exist
                    field['operators'] = {}
        return values

    def __call__(self):
        indexes = self.parseRegistry()
        indexes = self.getVocabularyValues(indexes)
        indexes = self.mapOperations(indexes)
        # todo: sortables
        return {
            'indexes': indexes,
            'sortable_indexes': {},
        }

