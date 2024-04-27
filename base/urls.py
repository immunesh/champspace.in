from .views import *
# from django.views.defaults import page_not_found

from django.urls import path


urlpatterns=[
    path('',dashboard,name='index'),
    path('logout/',logout,name='logout'),
    path('login/',login,name='login'),
    path('signup/',register,name='signup'),
    path('editProfile/',editprofile,name='editprofile'),
    path('viewprofile/<str:id>/',viewProfile,name='viewprofile')
    # path('/*',notfound,name='notfound')
]

handler404 = 'base.views.notfound'