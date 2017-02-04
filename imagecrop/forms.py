from django import forms
from django.utils.translation import ugettext_lazy as _

from .widgets import ImageCropWidget


class CroppedImageField(forms.MultiValueField):
    default_error_messages = {
        'invalid': _('Enter a valid cropped image.')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ImageCropWidget(kwargs['width'], kwargs['height'])
        fields = (
            forms.FileField(label=_('image'), required=False),
            forms.DecimalField(label=_('x1'), required=False),
            forms.DecimalField(label=_('y1'), required=False),
            forms.DecimalField(label=_('x2'), required=False),
            forms.DecimalField(label=_('y2'), required=False),
            forms.CharField(label=_('currrent file'), required=False),
        )
        super(CroppedImageField, self).__init__(fields)

    def compress(self, value_list):
        if value_list:
            return value_list
        return ''

    def clean(self, value):
        return value
