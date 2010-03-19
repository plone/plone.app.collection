from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator


class NonJavascriptValidator:
    """NonJavascriptValidator"""
    implements(IValidator)

    name = 'nonjavascriptvalidator'

    def __init__(self, name, title='', description=''):
        self.name = name

    def __call__(self, value, instance, *args, **kwargs):
        """
            Validates the given value
        """
        # value  is only empty when not using javascript
        if len(value) == 0:
            return u"Please finish your search terms / criteria"
        return 1

validatorList = [
    NonJavascriptValidator('javascriptDisabled', title='', description=''),
    ]

__all__ = ('validatorList', )
