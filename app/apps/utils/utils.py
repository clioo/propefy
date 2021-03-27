import base64
import imghdr
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from django.conf import settings
import geocoder


def get_file_name():
    return str(uuid.uuid4())


def get_file_extension(filename, decoded_file):
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
            raise ValidationError()

        extension = image.format.lower()

    extension = "jpg" if extension == "jpeg" else extension
    return extension


def convert_base6_to_image(base64_data):
    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
        "gif"
    )
    INVALID_FILE_MESSAGE = _("Please upload a valid image.")
    INVALID_TYPE_MESSAGE = _("The type of the image couldn't be determined.")
    # Strip base64 header.
    if ';base64,' in base64_data:
        header, base64_data = base64_data.split(';base64,')

    # Try to decode the file. Return validation error if it fails.
    try:
        decoded_file = base64.b64decode(base64_data)
    except (TypeError, binascii.Error, ValueError):
        raise ValidationError('Invalid format')
    # Generate file name:
    file_name = get_file_name()
    # Get the file name extension:
    file_extension = get_file_extension(file_name, decoded_file)
    if file_extension not in ALLOWED_TYPES:
        raise ValidationError(INVALID_TYPE_MESSAGE)
    complete_file_name = file_name + "." + file_extension
    data = ContentFile(decoded_file, name=complete_file_name)
    return data


def base64image_to_file(base64_data: str, extension='jpg'):
    if ';base64,' in base64_data:
        header, base64_data = base64_data.split(';base64,')

    # Try to decode the file. Return validation error if it fails.
    try:
        decoded_file = base64.b64decode(base64_data)
    except (TypeError, binascii.Error, ValueError):
        raise ValidationError('Error')
    # Generate file name:
    file_name = 'testi_image'
    # Get the file name extension:
    file_extension = 'jpg'
    if file_extension not in ['jpg']:
        raise ValidationError('Error')
    complete_file_name = file_name + "." + file_extension
    data = ContentFile(decoded_file, name=complete_file_name)
    return data


def cleaned_base_64(base64_image):
    try:
        return base64_image.split('base64,')[1]
    except Exception:
        return base64_image


def reverse_geolocaion(lat: float, lng: float) -> str:
    latlng = [lat, lng]
    g = geocoder.mapbox(latlng, method='reverse', key=settings.MAPBOX_TOKEN)
    raw_data = g.json.get('raw')
    if not raw_data:
        return "Unverified"
    place = raw_data.get('place')
    region = raw_data.get('region')
    country = raw_data.get('country')
    location = f'{place}, {region}, {country}'
    return location


class CreateListModelMixin(object):
    """Mixin that allows to create multiple objects from lists."""
    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CreateListModelMixin, self).get_serializer(*args,
                                                                **kwargs)
