from .views import *
# from django.views.defaults import page_not_found

from django.urls import path


urlpatterns=[
    path('',dashboard,name='index'),
    
    path('/*',notfound,name='notfound')
]

handler404 = 'base.views.notfound'