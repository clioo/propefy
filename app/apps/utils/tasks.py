from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email(mail_subject: str, message: str, to: list, **kwargs):
    email = EmailMessage(
        mail_subject, message, to=to,
        from_email=settings.EMAIL_HOST_USER
    )
    email.send()

@shared_task
def send_email_template(mail_subject: str, to: list,
                        template_name: str, context: dict, **kwargs):
    message = render_to_string(template_name, context)
    email = EmailMessage(
        mail_subject, message, to=to,
        from_email=settings.EMAIL_HOST_USER
    )
    email.content_subtype = "html"
    email.send()
