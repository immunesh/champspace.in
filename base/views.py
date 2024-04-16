from django.shortcuts import render,redirect
from django.http import HttpResponseNotFound
from django.contrib.auth import logout as djlogout,login as djlogin,authenticate
from .models import *
from django.contrib import messages


# Create your views here.
def dashboard(request):
    return render(request,'index.html')

def notfound(request, exception):
    response = HttpResponseNotFound()
    response.content = render('404.html', {}, request=request)
    return response

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usercheck=CustomUser.objects.filter(username=username)
        
        if len(usercheck)>0:


            user = authenticate(request,username=username,password=password)
            if user is not None:
                djlogin(request,user)
                messages.success(request,'Login Successful')
                return redirect('index')
            else:
                messages.error(request,'Password is Incorrect ')

                return redirect('login')
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('login')

    return render(request,'userlogin.html')
def register(request):
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password1']
        password2=request.POST['password2']
        if password==password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request,'Username already exists')
                return redirect('signup')
            else:
                CustomUser.objects.create_user(username=username,email=email,password=password)
                messages.success(request,'Account Created Successfully')
                return redirect('login')
        else:
            messages.error(request,'Passwords do not match')
            return redirect('signup')

    return render(request,'signup.html')


def logout(request):
    djlogout(request)
    return redirect('index')