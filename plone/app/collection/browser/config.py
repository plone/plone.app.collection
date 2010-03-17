# (temporary) Static config for plone.app.search
# ===================================================
# This has to be in the plone.app.registry later on. (preferable)

# CRITERION contains the searchable indexes and their operators and widgettypes
# SORTABLES contains the sortable indexes

# note: a view types a commented, because there is something about them
# see description/header per item



CRITERION={
    'Subject':{
        'title': 'Categories',
        'description': 'The category the item is put in.',
        'operators':{
            'is_not':{
                'title' : 'are not',
                'widget'        : 'MultipleSelectionWidget',
            },
            'is':{
                'title' : 'are',
                'widget'        : 'MultipleSelectionWidget',
            },
        },
        'values': {
            'Plone':{
                'title' : 'Plone',
            },
            'Zope':{
                'title' : 'Zope',
            },
            'Python':{
                'title' : 'Python',
            },
            'Javascript':{
                'title' : 'Javascript',
            },
        },
    },

    'Creator':{
        'title': 'Creator',
        'description': 'The creator of the item',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'StringWidget',
                'description'   : 'Only username search is supported.',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'StringWidget',
                'description'   : 'Only username search is supported',
            },
        },
    },

    'created':{
        'title': 'Creation date',
        'description': 'The time and date an item was created',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'Description':{
        'title': 'Description',
        'description': 'Description',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
        },
    },

    'effective':{
        'title': 'Effective date (publish date)',
        'description': 'The time and date an item becomes publicly available',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'end':{
        'title': 'End date (event)',
        'description': 'The end date and time of an event',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'expires':{
        'title': 'Expiration date',
        'description': 'The time and date an item is no longer publicly available',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'Type':{
        'title': 'Item type',
        'description': 'An item\'s type (e.g. Event)',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'MultipleSelectionWidget',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'MultipleSelectionWidget',
            },
        },
        'values': {
            'Page':{
                'title' : 'Page',
# possible extension/option
#               'preselected' : True,
            },
            'Folder':{
                'title' : 'Folder',
            },
            'File':{
                'title' : 'File',
            },
            'Collection':{
                'title' : 'Collection',
            },
        },
    },

    'path':{
        'title': 'Location (path)',
        'description': 'The location of an item in the site (path)',
        'operators':{
            'is':{
                'title' : 'location in the site',
                'widget'        : 'ReferenceWidget',
                'description'   : 'Fill in your absolute location e.g.: /site/events/',
            },
            'relative_location':{
                'title' : 'location in site relative to the current location',
                'widget'        : 'RelativePathWidget',
                'description'   : 'Enter a relative path e.g.:\'..\' for the parent folder \'../..\' for the parent\'s parent \'../somefolder\' for a sibling folder',
            },
        },
    },

    'modified':{
        'title': 'Modification date',
        'description': 'The time and date an item was last modified',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'getRawRelatedItems':{
        'title': 'Related to',
        'description': 'Find items related to the selected items',
        'operators':{
            'to':{
                'title' : 'to',
                'widget'        : 'MultipleSelectionWidget',
            },
        },
    },

    'SearchableText':{
        'title': 'Search text',
        'description': 'Text search of an item\'s contents',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
        },
    },

    'getId':{
        'title': 'Short name',
        'description': 'Short name of the item',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'StringWidget',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'StringWidget',
            },
        },
    },

    'start':{
        'title': 'Start date',
        'description': 'The start date and time of an event',
        'operators':{
            'less_then':{
                'title': 'before',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'is':{
                'title': 'on',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'larger_then':{
                'title': 'after',
                'widget': 'DateWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
            'between':{
                'title': 'between',
                'widget': 'DateRangeWidget',
                'description'   : 'please use YYYY/MM/DD.',
            },
        },
    },

    'review_state':{
        'title': 'State',
        'description': 'An item\'s workflow state (e.g.published)',
        'operators':{
            'is_not':{
                'title' : 'does not equal',
                'widget'        : 'MultipleSelectionWidget',
            },
            'is':{
                'title' : 'equals',
                'widget'        : 'MultipleSelectionWidget',
            },
        },
        'values': {
            'Published':{
                'title' : 'Published',
            },
            'Private':{
                'title' : 'Private',
            },
            'Pending':{
                'title' : 'Pending',
            },
            'Rejected':{
                'title' : 'Rejected',
            },
            'Sent_back':{
                'title' : 'Sent Back',
            },
            'Draft':{
                'title' : 'Draft',
            },
        },
    },

    'Title':{
        'title': 'Title',
        'description': 'Title of the item',
        'operators':{
            'plone.app.collection.operation.string.is_not':{
                'title' : 'does not equal',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
            'plone.app.collection.operation.string.is':{
                'title' : 'equals',
                'widget'        : 'StringWidget',
                'description'   : 'Tip: you can use * to autocomplete.',
            },
        },
    },
}


SORTABLES={
    'Creator':{
        'title' : 'Creator',
        'description' : 'The person that created an item',
    },
    'Type':{
        'title' : 'Item Type',
        'description' : 'The content type of the item',
    },
# is there an usecase?
#     'getId':{  
#          'title' : 'Short name',
#          'description' : 'The short name of the item',
#     },
# same as getId?
#     'id':{  
#          'title' : 'ID',
#          'description' : '',
#     },
# this is portal type, such as document (not page), topic (not collection)
#     'portal_type':{  
#          'title' : '',
#          'description' : '',
#     },
    'review_state':{  
        'title' : 'Workflow state',
        'description' : 'An item\'s workflow state (e.g.published)',
    },
    'sortable_title':{  
        'title' : 'Title',
        'description' : 'The item\'s title transformed for sorting',
    },
# Same as Modification Date?
#     'Date':{  
#          'title' : 'Date',
#          'description' : '',
#     },
    'created':{  
        'title' : 'Creation date',
        'description' : 'The time and date an item was created',
    },
    'effective':{  
        'title' : 'Effective date',
        'description' : 'The time and date an item was published',
    },
    'end':{  
        'title' : 'End date (Event)',
        'description' : 'The end date and time of an event',
    },
    'expires':{  
        'title' : 'Expiry date',
        'description' : 'The time and date an item is no longer publicly available',
    },
    'modified':{  
        'title' : 'Modification date',
        'description' : 'The time and date an item was last modified',
    },
    'start':{  
        'title' : 'Start date',
        'description' : 'The start date and time of an event',
    },
    'Subject':{  
        'title' : 'Category',
        'description' : 'The keywords used to describe an item',
    },
    'getEventType':{  
        'title' : 'Event type',
        'description' : 'The type of event',
    },
# use case?
#     'getRawRelatedItems':{  
#          'title': 'Related to',
#          'description': 'Find items related to the selected items',
#     },
    'relevance':{
        'title' : 'Relevance',
        'description' : 'Relevance',
    },
}
