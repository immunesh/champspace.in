from django.shortcuts import render,redirect
from django.http import HttpResponseNotFound
from django.contrib.auth import logout as djlogout,login as djlogin,authenticate
from .models import *
from django.contrib import messages


# Create your views here.
def dashboard(request):
    return render(request,'beta_admin/index.html')

def notfound(request, exception):
    response = HttpResponseNotFound()
    response.content = render('beta_admin/404.html', {}, request=request)
    return response
