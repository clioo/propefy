from celery import shared_task
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import datetime
from apps.core.models import SpamEmail, User, HistorialBusquedas, Inmueble
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point


@shared_task
def send_email(mail_subject: str, message: str, to: list, **kwargs):
    email = EmailMessage(
        mail_subject, message, to=to,
        from_email=settings.EMAIL_HOST_USER
    )
    email.send()


@shared_task
def send_recommendation_emails():
    for user in User.objects.filter(is_active=True):
        results = []
        last_spam = SpamEmail.objects.filter(
            user=user).order_by('created').first()
        if last_spam:
            last_spam = last_spam.created
        else:
            today = datetime.datetime.now()
            days = datetime.timedelta(days=30)
            last_spam = today - days

        historiales = HistorialBusquedas.objects.filter(user=user,
            created__gte=last_spam)
        for historial in historiales:
            kwargs = {
                'recamaras': historial.recamaras,
                'precio__gte': historial.precio_min,
                'precio__lte': historial.precio_max,
                'estado': historial.estado,
                'full_text': historial.full_text,
                'titulo': historial.titulo,
                'descripcion': historial.descripcion,
                'categoria': historial.categoria,
                'tipo_propiedad': historial.tipo_propiedad,
            }
            distance = None
            if historial.latitude is not None and historial.longitude is not None:
                longitude = historial.latitude
                latitude = historial.longitude
                distance_kms = 10
                distance = Distance('point',
                    Point(float(latitude), float(longitude), srid=4326))
            for key in kwargs.keys():
                if kwargs[key] is None:
                    kwargs.pop(key)
            inmuebles = Inmueble.objects.filter(**kwargs)
            if distance:
                inmuebles = inmuebles.annotate(
                    distance=distance
                ).order_by('distance').filter(distance__lte=distance_kms)
            results.extend(inmuebles)


@shared_task
def send_email_template(mail_subject: str, to: list,
                        template_name: str, context: dict, **kwargs):
    # message = render_to_string(template_name, context)
    email = EmailMessage(to=to,
        from_email='jesus_acosta1996@hotmail.com'
    )
    email.template_id = template_name
    email.dynamic_template_data = context
    email.send(fail_silently=False)
