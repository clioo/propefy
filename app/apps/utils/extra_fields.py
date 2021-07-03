import base64
import binascii
import imghdr
import io
import uuid
from PIL import Image

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import (ImageField)
from rest_framework.response import Response
from rest_framework import serializers
from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES


DEFAULT_CONTENT_TYPE = "application/octet-stream"


class ListFilter(filters.Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        lookup = '%s__%s' % (self.field_name, 'in')
        value = value.split(',')
        qs = self.get_method(qs)(**{lookup: value})
        return qs


class Base64FieldMixin(object):
    @property
    def ALLOWED_TYPES(self):
        raise NotImplementedError

    @property
    def INVALID_FILE_MESSAGE(self):
        raise NotImplementedError

    @property
    def INVALID_TYPE_MESSAGE(self):
        raise NotImplementedError

    EMPTY_VALUES = (None, '', [], (), {})

    def __init__(self, *args, **kwargs):
        self.represent_in_base64 = kwargs.pop('represent_in_base64', False)
        super(Base64FieldMixin, self).__init__(*args, **kwargs)

    def obtain_optimized_image(self, decoded_file, complete_file_name,
                               file_extension) -> ContentFile:
        buf = io.BytesIO(decoded_file)
        img = Image.open(buf)
        img.thumbnail(self.max_image_size)
        img_byte_arr = io.BytesIO()
        if file_extension == 'jpg':
            file_extension = 'jpeg'
        img.save(img_byte_arr, format=file_extension)
        return ContentFile(img_byte_arr.getvalue(), name=complete_file_name)

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, str):
            # Strip base64 header.
            if ';base64,' in base64_data:
                header, base64_data = base64_data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)
            # Generate file name:
            file_name = self.get_file_name()
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)
            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)
            complete_file_name = file_name + "." + file_extension
            data = self.obtain_optimized_image(decoded_file,
                                               complete_file_name,
                                               file_extension)
            return super(Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError(_('Invalid type. This is not an base64 string: {}'.format(
            type(base64_data))))

    def get_file_extension(self, filename, decoded_file):
        raise NotImplementedError

    def get_file_name(self):
        return str(uuid.uuid4())

    def to_representation(self, file):
        if self.represent_in_base64:
            # If the underlying ImageField is blank, a ValueError would be
            # raised on `open`. When representing as base64, simply return an
            # empty base64 str rather than let the exception propagate unhandled
            # up into serializers.
            if not file:
                return ''

            try:
                with open(file.path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                raise IOError("Error encoding file")
        else:
            return super(Base64FieldMixin, self).to_representation(file)


class Base64ImageField(Base64FieldMixin, ImageField):
    """
    A django-rest-framework field for handling image-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    """
    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
        "gif"
    )
    INVALID_FILE_MESSAGE = _("Please upload a valid image.")
    INVALID_TYPE_MESSAGE = _("The type of the image couldn't be determined.")

    def get_file_extension(self, filename, decoded_file):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow is not installed.")
        extension = imghdr.what(filename, decoded_file)

        # Try with PIL as fallback if format not detected due
        # to bug in imghdr https://bugs.python.org/issue16512
        if extension is None:
            try:
                image = Image.open(io.BytesIO(decoded_file))
            except (OSError, IOError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            extension = image.format.lower()

        extension = "jpg" if extension == "jpeg" else extension
        return extension


class HdBase64ImageField(Base64ImageField):
    max_image_size = (1080, 1080)


class ThumbnailBase64ImageField(Base64ImageField):
    max_image_size = (100, 100)


class CurrentUserDefault(object):
    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user

    def __call__(self):
        return self.user

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class PatchModelMixin(object):
    """
    Update a model instance.
    """
    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class RelatedFieldObjectRetriever(serializers.PrimaryKeyRelatedField):
    """Retrieves a serialized object from a PrimaryKeyRelatedField"""
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)
