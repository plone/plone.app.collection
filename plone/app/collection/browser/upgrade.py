import sys
import traceback
import logging

import transaction

from Acquisition import aq_parent
from zope.component.hooks import getSite
from zope.component import getUtility

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from plone.app.querystring.interfaces import IQuerystringRegistryReader


logger = logging.getLogger('plone.app.collection')
prefix = "plone.app.querystring"

INVALID_OPERATION = 'Invalid operation %s for criterion: %s'


class Erreur(object):
    def __init__(self, ob, exception=None, traceback=None, messages=None):
        self.ob = ob
        self.exception = exception
        self.traceback = traceback
        self.messages = messages

    def getStacktrace(self):
        if not self.traceback:
            return ""

        def format(line):
            return "Module %s, line %s, in %s, %s" % line
        return map(format, self.traceback)


# Convertors
def ATDateCriteria(formquery, criterion, registry):
    operator = {'max': 'lessThan',
                'min': 'moreThan', }
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.date.%s" % (prefix, operator[value['range']])

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value['query'].ISO8601()}
        formquery.append(row)
    return messages


def ATSimpleStringCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.string.contains" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value['query']}
        formquery.append(row)
    return messages


def ATCurrentAuthorCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        operations = registry.get('%s.field.%s.operations' % (prefix, index))
        operation = "%s.operation.string.currentUser" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value}
        formquery.append(row)
    return messages


def ATListCriterion(formquery, criterion, registry):
    messages = []
    for index, value in criterion.getCriteriaItems():
        key = '%s.field.%s.operations' % (prefix, index)
        operations = registry.get(key)
        operation = "%s.operation.list.contains" % prefix

        if not operation in operations:
            msg = INVALID_OPERATION % (operation, criterion)
            messages.append(msg)
            continue

        row = {'i': index,
               'o': operation,
               'v': value['query']}
        formquery.append(row)
    return messages


class Upgrade(BrowserView):
    """ Allow upgrading old ATTopic collections to
        new plone.app.collection collections

    TODO This approach misses things like setting the Author,
    modification date, marker interfaces, archetypes.schemaextender
    extensions, etcetera.  Products.contentmigration may be a better
    basis.
    """

    def __call__(self):
        self.failed = []

        site = getSite()
        # Allow collections globally
        pt = getToolByName(site, 'portal_types')
        old_global_allow = pt['Collection'].global_allow
        pt['Collection'].global_allow = True

        import pdb; pdb.set_trace()
        for path in self.request.get('paths', []):
            try:
                ob = site.restrictedTraverse(path)
                messages = self.convert(ob)
                if messages:
                    error = Erreur(ob=ob, messages=messages)
                    self.failed.append(error)
            except Exception, e:
                raise
                tb = traceback.extract_tb(sys.exc_info()[2])
                error = Erreur(ob=ob, exception=e, traceback=tb)
                self.failed.append(error)

        pt['Collection'].global_allow = old_global_allow

        submitted = self.request.get('submitted', False)
        dry_run = self.request.get('dry_run', False)
        if not submitted or dry_run:
            transaction.abort()

        return self.index()

    def getCollections(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'Topic',
                 'path': '/'.join(self.context.getPhysicalPath()), }
        return catalog(query)

    def convert(self, ob):
        messages = []
        path = "/".join(ob.getPhysicalPath())
        logger.info('Converting object %s at %s' % (ob, path))

        old_id = ob.id

        # Create new collection at id = '%s-new' % id
        parent = aq_parent(ob)

        # Allow collection to be added
        pt = getToolByName(parent, 'portal_types')
        myType = pt.getTypeInfo(parent)
        old_fct = myType.filter_content_types
        myType.filter_content_types = False

        # Add Collection
        id = parent.invokeFactory(type_name="Collection", id='%s-new' % old_id)
        new_ob = parent[id]

        # Set old values
        myType.filter_content_types = old_fct

        # Set criteria
        # See also Products.ATContentTypes.content.topic.buildQuery
        criteria = ob.listCriteria()
        formquery = []
        for criterion in criteria:
            type_ = criterion.__class__.__name__
            module = 'plone.app.collection.browser.upgrade'
            fromlist = module.split(".")[:-1]
            try:
                module = __import__(module, fromlist=fromlist)
                convertor = getattr(module, type_)
            except (ImportError, AttributeError):
                messages.append('Unsupported criterion %s' % type_)
                continue
            else:
                reg = getUtility(IRegistry)
                reader = IQuerystringRegistryReader(reg)
                result = reader.parseRegistry()

                messages_ = convertor(formquery, criterion, result)
                messages.extend(messages_)

        logger.info("formquery: %s" % formquery)
        new_ob.setQuery(formquery)

        # Set collection attributes
        new_ob.setTitle(ob.Title())
        new_ob.setText(ob.getText())
        new_ob.setLimitNumber(ob.getLimitNumber())
        new_ob.setItemCount(ob.getItemCount())

        # set UID for link-by-uid etc
        new_ob._setUID(ob.UID())

        # Set Plone attributes
        layout = ob.getLayout()
        # TODO Check the available view methods and only change the
        # layout if it is not available for the new collection.
        layout = 'standard_view' if layout == 'atct_topic_view' else layout
        new_ob.setLayout(layout)

        # Set workflow
        if False:
            pw = getToolByName(self.context, 'portal_workflow')
            state = pw.getInfoFor(ob, 'review_state')

            # get possible transitions for object in current state
            transitions = [x['transition']
                           for x in pw.getActionsFor(new_ob)
                           if 'transition' in x]

            # find transition that brings us to the state of parent object
            for item in transitions:
                if item.new_state_id == state:
                    pw.doActionFor(new_ob, item.id)
                    break

        # remove old collection
        # Make sure we have _p_jar
        if False:
            transaction.savepoint(optimistic=True)
            parent.manage_delObjects([old_id, ])

            # rename, reindex etc
            parent.manage_renameObject(id, old_id)
            new_ob.unmarkCreationFlag()
            new_ob.reindexObject()

        return messages
