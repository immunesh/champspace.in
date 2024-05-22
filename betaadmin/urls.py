from django.urls import path
from .views import *

urlpatterns=[
    path('',home,name='beta'),
    path('inbox/',inbox,name='inbox'),
    path('dashboard/',dashboard,name='dashboard'),
    path('mycourses/',mycourses,name='mycourses'),
    path('courses/',courses,name='courses'),
    path('admin/edit-course/<str:pk>/',courseedit,name='editcourse'),
    path('admin/del-course/<str:pk>/',delcourse,name='deletecourse'),
    path('admin/del-user/<str:pk>/',deluser,name='del-user'),
    path('admin/users/',userlist,name="userslist"),path('admin/user/create/',usercreation,name='usercreate'),
    path('mysubscriptions/',subscriptions,name='subscription'),
    path('quiz/',quiz,name='quiz'),
    path('settings/',settings,name='settings'),
    path('admin/', admindashboard, name='admin'),
    path('admin/courses',admincourses,name="admincourses"),
    path('admin/course/<str:pk>/',admincourseadd,name='admincourseAM'),
    path('logout/',logout,name='logout'),
    path('login/',login,name='login'),
    path('signup/',register,name='signup'),
    path('editProfile/',editprofile,name='editprofile'),
    path('viewprofile/<str:id>/',viewProfile,name='viewprofile'),
    path('forgot-password/',forget,name='forgot'),
    path('forgot-password/<token>/',forgotreset,name='reset')
]