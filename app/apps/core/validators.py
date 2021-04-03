import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_images(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported image extension.'))


def validate_file_video(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp4', '.flv', '.wmp']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported video extension.'))
