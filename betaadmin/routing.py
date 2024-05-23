from django.urls import path
from .consumers import Chatconsumer
websocket_urlpatterns= [
    path('beta/getmessages/<str:pk>/',Chatconsumer.as_asgi()),
]