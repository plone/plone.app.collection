from types import ListType, TupleType

from zope.contenttype import guess_content_type

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.utils import mapply
from Products.Archetypes.Marshall import RFC822Marshaller, parseRFC822, formatRFC822Headers


class CollectionRFC822Marshaller(RFC822Marshaller):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess('deny')

    def demarshall(self, instance, data, **kwargs):
        # We don't want to pass file forward.
        if 'file' in kwargs:
            if not data:
                # TODO Yuck! Shouldn't read the whole file, never.
                # OTOH, if you care about large files, you should be
                # using the PrimaryFieldMarshaller or something
                # similar.
                data = kwargs['file'].read()
            del kwargs['file']
        headers, body = parseRFC822(data)
        
        query = {}
        for k, v in headers.items():
            if not k.startswith("query"):
                continue
            else:
                index = int(k[5])
                sub_key = k.split("_")[1]
                query_part = query.get(index, {})
                query_part[sub_key] = v
                query[index] = query_part
                del headers[k]
        query = [facet[1] for facet in sorted(query.items())]
        
        header = formatRFC822Headers(headers.items())
        data = '%s\n\n%s' % (header, body)
        
        try:
            return RFC822Marshaller.demarshall(self, instance, data, **kwargs)
        finally:
            instance.query = query

    def marshall(self, instance, **kwargs):
        content_type, length, data = RFC822Marshaller.marshall(self, instance, **kwargs)
        headers, body = parseRFC822(data)
        
        headers = headers.items()
        for i, query in enumerate(instance.query):
            for key, value in query.items():
                if isinstance(value, list):
                    value = "\n".join(value)
                header_key = 'query%d_%s' % (i, key)
                headers.append((header_key, value))
        
        header = formatRFC822Headers(headers)
        data = '%s\n\n%s' % (header, body)
        length = len(data)
        return (content_type, length, data)

InitializeClass(CollectionRFC822Marshaller)