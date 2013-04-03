from Products.CMFCore.utils import getToolByName


def enable_syndication(obj, event):
    # Enable syndication by default
    syn_tool = getToolByName(obj, 'portal_syndication', None)
    if syn_tool is not None:
        if (syn_tool.isSiteSyndicationAllowed() and
                not syn_tool.isSyndicationAllowed(obj)):
            syn_tool.enableSyndication(obj)
