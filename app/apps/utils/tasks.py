from celery import shared_task
from django.db.utils import Error
from apps.core import models
from .utils import get_file_extension, cleaned_base_64, get_file_name
from PIL import Image
import base64
import io
from django.core.files.base import ContentFile


@shared_task
def generate_thumbnail_from_base64(b64_image: str, model_target: str,
                                   id_target: int):
    available_models = {
        'user': models.User.objects,
        'mmr': models.MMR.objects,
        'business': models.Business.objects
    }
    if model_target not in available_models.keys():
        raise NotImplementedError
    rows = available_models[model_target].filter(id=id_target)
    if not rows.exists():
        raise Error
    instance = rows.first()
    b64_image = cleaned_base_64(b64_image)
    msg = base64.b64decode(b64_image)
    file_name = get_file_name()
    extension = get_file_extension(file_name, msg)
    buf = io.BytesIO(msg)
    img = Image.open(buf)
    img.thumbnail((400, 400))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=extension)
    complete_file_name = file_name + "." + extension
    thumbnail = ContentFile(img_byte_arr.getvalue(), name=complete_file_name)
    instance.thumbnail = thumbnail
    instance.save()
    
