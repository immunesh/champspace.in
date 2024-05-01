from django.shortcuts import render,redirect
from django.http import HttpResponseNotFound
from django.contrib.auth import logout as djlogout,login as djlogin,authenticate
from .models import *
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Create your views here.
def dashboard(request):
    return render(request,'beta_admin/index.html')

def notfound(request, exception):
    response = HttpResponseNotFound()
    response.content = render('beta_admin/404.html', {}, request=request)
    return response

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        level=request.POST['level']
        usercheck=CustomUser.objects.filter(username=username)
        
        if len(usercheck)>0:


            user = authenticate(request,username=username,password=password)
            
            if user is not None:
                
                
                
                if level == '1':
                    if BetaUser.objects.filter(user=user).exists():
                        messages.success(request,'Login Successful')
                        djlogin(request,user)
                        return redirect('index')
                    else:
                        messages.error(request,"You are not a member")
                        return redirect('login')
                if level == '2':
                    if GammaUser.objects.filter(user=user).exists():
                        messages.success(request,'Login Successful')
                        djlogin(request,user)
                        return redirect('gamma')
                    else:
                        messages.error(request,"You are not a member")
                        return redirect('login')
            else:
                messages.error(request,'Password is Incorrect ')

                return redirect('login')
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('login')

    return render(request,'beta_admin/userlogin.html')
def register(request):
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password1']
        level=request.POST['level']
        password2=password
        if not level=='0':

            if password==password2:
                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request,'Username already exists')
                    return redirect('signup')
                else:
                    user=CustomUser.objects.create_user(username=username,email=email,password=password)
                    if level == '1':
                        BetaUser.objects.create(user=user)
                    if level == '2':
                        GammaUser.objects.create(user=user)
                        
                    messages.success(request,'Account Created Successfully')
                    return redirect('login')
            else:
                messages.error(request,'Passwords do not match')
                return redirect('signup')

    return render(request,'beta_admin/signup.html')


def logout(request):
    djlogout(request)
    return redirect('index')
def viewProfile(request,id):
    user=CustomUser.objects.get(id=id)
    betauser=BetaUser.objects.get(user=user)
    return render (request,'beta_admin/viewprofile.html',{'user':user,'betauser':betauser})
def editprofile(request):
    user=request.user
    betauser=BetaUser.objects.get(user=user)
    if request.method== 'POST':
        if request.FILES.get('profilepic'):
            betauser.profilepic=request.FILES['profilepic']
            
        user.first_name=request.POST['first']
        user.last_name=request.POST['last']
        user.email=request.POST['email']

        betauser.phone=request.POST['phone']
        betauser.birthday=request.POST['birthday']
        betauser.website=request.POST['website']
        
        user.save()
        betauser.save()
        messages.success(request,'Profile Updated Successfully')
        return redirect('editprofile')
    
    return render(request,'beta_admin/editprofile.html',{'user':user,'betauser':betauser})