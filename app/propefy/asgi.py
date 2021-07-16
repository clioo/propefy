"""
ASGI config for propefy project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from django.core.asgi import get_asgi_application
from apps.user.consumers import MyConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propefy.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"^frontend/$", MyConsumer.as_asgi())
        ])
    ),
})

