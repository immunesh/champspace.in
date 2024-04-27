from django.urls import path
from .views import *

urlpatterns=[
    path('', gammaAdmin, name='gamma'),
    path('messages/', gammaMessages, name='gammaMessages'),
]