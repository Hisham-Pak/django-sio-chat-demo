"""
ASGI config for proj project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

import chatapp.routing

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            chatapp.routing.urlpatterns +
            [
                re_path("", django_asgi_app),
            ]
        ),
        "websocket": URLRouter(chatapp.routing.urlpatterns),
    }
)
