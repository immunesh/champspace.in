from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('sign-in/', views.signIn, name='sign-in'),
    path('registration/', views.signUp, name='registration'),
    path('forget-password/', views.forget_password, name='forget-password'),
    path('student-dashboard/',views.student_dashboard, name='student-dashboard'),
]
