from django.urls import path
from .views import *

urlpatterns=[
    path('', gammaUser, name='gamma'),
    path('messages/', gammaMessages, name='gammaMessages'),
    path('chat/', gammaChat, name='gammaChat'),
]