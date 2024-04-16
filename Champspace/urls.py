
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    
    path('',include('base.urls')),
    path('admin/',include('customadmin.urls')),
    path('djangoadmin/', admin.site.urls),
]
