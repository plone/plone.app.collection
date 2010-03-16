class CollectionRegistryReader(object):

    def __init__(self, registry):
        self.registry = registry

    def __call__(self):
        """Make a dictionary structure for the values in the registry"""
        result = {}
        for record in self.registry.records:
            name = record.split('plone.app.collection.')[1]
            splitted = name.split('.')
            current = result
            for x in splitted[:-1]:
                if not x in current:
                    # create the key if it's not there
                    current[x] = {}
                current = current[x]
            key = splitted[-1]
            current[key] = self.registry.records[record].value
        return result

        