from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .forms import CroppedImageField as CroppedImageFormField
from .models import CroppedImage

import os
import uuid


class CroppedImageInstance(object):
    def __init__(self, image, x1, y1, x2, y2, q, zoom, maxw, maxh):
        self.image = image
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.q = q
        self.zoom = zoom
        self.maxw = maxw
        self.maxh = maxh

    def __len__(self):
        return 512

    def cropped_url(self):
        return CroppedImage.get_cropped_image(
            path=os.path.join(settings.MEDIA_ROOT, self.image),
            x1=self.x1, y1=self.y1,
            x2=self.x2, y2=self.y2,
            q=self.q,
            zoom=1,
            maxw=self.maxw, maxh=self.maxh
        ).url

    def original_url(self):
        return settings.MEDIA_URL + self.image


class CroppedImageField(models.CharField):
    description = _("A cropped image")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 512)
        self.upload_to = kwargs.pop('upload_to', None)

        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.aspect = 1
        if self.height is not None and self.width is not None:
            self.aspect = self.width / self.height

        self.quality = kwargs.pop('quality', 95)
        self.zoom = kwargs.pop('zoom', 1)

        super(CroppedImageField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None or value == '':
            return None

        image, x1, y1, x2, y2, q, zoom = value.split(';')
        return CroppedImageInstance(image, x1, y1, x2, y2, q, zoom, self.width,
                                    self.height)

    def to_python(self, value):
        print('PY VALUE', value)
        if value is None:
            return None

        if isinstance(value, list):
            image, x1, y1, x2, y2, prev_value = value
            if image is None:
                image = prev_value
            return CroppedImageInstance(image, x1, y1, x2, y2, self.quality,
                                        self.zoom, self.width, self.height)
        else:
            assert('This should never happen!')

    def get_filename(self):
        return os.path.join(self.upload_to, str(uuid.uuid4()) + '.jpg')

    def get_prep_value(self, value):
        print('PREP VALUE', value)
        if isinstance(value, CroppedImageInstance):
            if isinstance(value.image, UploadedFile):
                filename = self.get_filename()
                default_storage.save(filename, ContentFile(
                    value.image.read()))
            else:
                print('IMG val', value.image)
                filename = value.image

            result = '{image};{x1};{y1};{x2};{y2};{q};{zoom}'.format(
                image=filename, x1=value.x1, y1=value.y1, x2=value.x2,
                y2=value.y2, q=value.q, zoom=value.zoom)
            return result
        return None

    def formfield(self, **kwargs):
        defaults = {
            'form_class': CroppedImageFormField,
            'width': self.width,
            'height': self.height,
        }
        defaults.update(kwargs)
        return super(CroppedImageField, self).formfield(**defaults)
