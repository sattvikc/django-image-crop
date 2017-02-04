from django import forms
from django.conf import settings
from django.template.loader import render_to_string

import uuid


class ImageCropWidget(forms.MultiWidget):
    def __init__(self, width, height, aspect=None, attrs=None):
        uid = str(uuid.uuid4())
        self.uid = uid

        widgets = (
            forms.FileInput(attrs={'class': 'cropit-image-input',
                                   'data-imagecrop-file': uid}),
            forms.HiddenInput(attrs={'class': 'x1', 'data-imagecrop-x1': uid}),
            forms.HiddenInput(attrs={'class': 'y1', 'data-imagecrop-y1': uid}),
            forms.HiddenInput(attrs={'class': 'x2', 'data-imagecrop-x2': uid}),
            forms.HiddenInput(attrs={'class': 'y2', 'data-imagecrop-y2': uid}),
            forms.HiddenInput(attrs={'class': 'previous_value'}),
        )
        self.width = width
        self.height = height
        self.image = None
        self.x1 = self.y1 = self.x2 = self.y2 = 0
        super(ImageCropWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value is None:
            return [None, None, None, None, None, None, None, None]

        if isinstance(value, str):
            value = value.split(';')
            self.image = settings.MEDIA_URL + value[0]
            self.x1 = float(value[1])
            self.y1 = float(value[2])
            self.x2 = float(value[3])
            self.y2 = float(value[4])
            self.q = float(value[5])
            self.zoom = float(value[6])
            return [
                self.image,
                self.x1, self.y1,
                self.x2, self.y2,
                value[0]
            ]
        else:
            self.image = settings.MEDIA_URL + value.image
            self.x1 = value.x1
            self.y1 = value.y1
            self.x2 = value.x2
            self.y2 = value.y2
            self.q = value.q
            self.zoom = value.zoom
            return [
                self.image,
                self.x1, self.y1,
                self.x2, self.y2,
                value.image
            ]

    def format_output(self, rendered_widgets):
        print('IMAGE', self.image)
        return render_to_string('imagecrop/widgets/imagecrop.html', {
            'id': self.uid,
            'width': self.width,
            'height': self.height,
            'aspect': self.width / self.height,
            'widgets': {
                'image': rendered_widgets[0],
                'x1': rendered_widgets[1],
                'y1': rendered_widgets[2],
                'x2': rendered_widgets[3],
                'y2': rendered_widgets[4],
                'prev': rendered_widgets[5],
            },
            'state': {
                'image': self.image,
                'x1': self.x1,
                'y1': self.y1,
                'x2': self.x2,
                'y2': self.y2,
            }
        })

    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js',
            'https://npmcdn.com/imagecrop@1.0.4/dist/index.umd.min.js',
            'imagecrop/main.js',
        )
        css = {}
