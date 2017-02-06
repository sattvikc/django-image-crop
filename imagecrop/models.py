from django.conf import settings
from django.db import models

from PIL import Image

import os
import uuid


class CroppedImage(models.Model):
    IMAGE_PATH = 'cropped-images/images/'
    image = models.FileField(upload_to=IMAGE_PATH, null=True,
                             blank=True)
    path = models.CharField(max_length=1024, blank=True)
    key = models.CharField(max_length=2048, unique=True)

    @staticmethod
    def get_new_file_name(root):
        while True:
            fname = str(uuid.uuid4()) + '.jpg'
            if not os.path.exists(os.path.join(root, fname)):
                return fname

    @classmethod
    def get_cropped_image(cls, path, x1, y1, x2, y2, q=95, zoom=1, maxw=1920,
                          maxh=1920):
        x1 = float(x1)
        y1 = float(y1)
        x2 = float(x2)
        y2 = float(y2)
        q = int(q)
        zoom = float(zoom)
        key = '{path}|{x1}|{y1}|{x2}|{y2}|{q}|{zoom}|{maxw}|{maxh}'.format(
            path=path, x1=x2, y1=y1, x2=x2, y2=y2, q=q, zoom=zoom, maxw=maxw,
            maxh=maxh
        )

        try:
            # Return if image already exists
            return cls.objects.get(key=key).image
        except:
            imgcrop = cls(key=key, path=path)
            im = Image.open(path)
            iw, ih = im.size
            x1 = round(iw * x1 / 100)
            y1 = round(ih * y1 / 100)
            x2 = round(iw * x2 / 100)
            y2 = round(ih * y2 / 100)

            im = im.crop((x1, y1, x2, y2))

            w = round((x2 - x1) * zoom)
            h = round((y2 - y1) * zoom)

            if w > maxw:
                h = round(h * maxw / w)
                w = maxw
            if h > maxh:
                w = round(w * maxh / h)
                h = maxh

            im = im.resize((w, h), Image.ANTIALIAS)

            fname = CroppedImage.get_new_file_name(os.path.join(
                settings.MEDIA_ROOT, cls.IMAGE_PATH))
            fpath = os.path.join(settings.MEDIA_ROOT, cls.IMAGE_PATH, fname)

            if not os.path.exists(os.path.dirname(fpath)):
                os.makedirs(os.path.dirname(fpath))

            im.convert('RGB').save(fpath, 'JPEG', quality=q)
            imgcrop.image = os.path.join(cls.IMAGE_PATH, fname)
            imgcrop.save()
        return cls.objects.get(key=key).image
