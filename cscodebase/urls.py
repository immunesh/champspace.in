from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('sign-up/', views.signUp, name='sign-up'),
    path('home/', views.home, name='home'),  # Example home view
]
