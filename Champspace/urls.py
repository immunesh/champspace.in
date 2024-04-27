
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    
    path('beta/',include('base.urls')),
    path('gamma/', include('gamma.urls')),
    path('betaadmin/',include('betaadmin.urls')),
    path('djangoadmin/', admin.site.urls),
]
