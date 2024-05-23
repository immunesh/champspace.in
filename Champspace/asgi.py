"""
ASGI config for Champspace project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Champspace.settings')
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
from betaadmin import routing

django.setup()

application = ProtocolTypeRouter(
    {
        'http':get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    }
)


