
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    
    path('',include('base.urls')),
    path('gamma-user/', include('gamma.urls')),
    path('gamma-admin/', include('gammaadmin.urls')),
    path('beta/',include('betaadmin.urls')),
    path('djangoadmin/', admin.site.urls),
    
]