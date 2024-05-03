# Create your views here.
from django.shortcuts import render,redirect
from base.models import CustomUser,Course,isPurchased
from collections import defaultdict

from django.http import HttpResponseNotFound
from django.contrib.auth import logout as djlogout,login as djlogin,authenticate
from base.models import *

from django.contrib import messages
# Create your views here.
def admindashboard(request):
    users=CustomUser.objects.all().order_by('-date_joined')
    
    month_wise_joined = defaultdict(int)
    month_wise_active = defaultdict(int)
    activelist=[]
    joinedlist=[]
    monthlist=''
    for user in users:
            
        string1 = user.date_joined
        month_wise_joined[string1.strftime('%b')] += 1
        month_wise_active[user.last_login.strftime('%b')] +=1
    for key,values in month_wise_joined.items():
        monthlist+=key+","
        joinedlist.append(values)
    for key,values in month_wise_active.items():
        activelist.append(values)
    recentJoinedusers=users[:5]
    courses=Course.objects.all().order_by('-course_createdon')
    purchased=isPurchased.objects.all().order_by('-purchased_on')
    data=[users.count(),purchased.count()]
    earnings=defaultdict(int)
    month=''
    for purchases in purchased:
        if month=='' or month == purchases.purchased_on.strftime('%b'):
            
            earnings[purchases.purchased_on.strftime('%b')]+=purchases.course.course_price
            
            month=purchases.purchased_on.strftime('%b')
        
    profit=[]
    for key,values in earnings.items():
        profit.append(key)
        
        profit.append(values)
    totalearnings=0
    for purchases in purchased:
        totalearnings+=purchases.course.course_price
    
    context = {'activedata':activelist,
               'joineddata':joinedlist,
               'months':monthlist[:-1],
               'recentUsers':recentJoinedusers,
               'courses':courses,
               'breakchartdata':data,
               'profit':profit[1],
               'profitmonth':profit[0],
               'totalearn':totalearnings
               }

    return render(request,'beta_admin/admin/dashboard.html', context=context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        
        usercheck=CustomUser.objects.filter(username=username)
        
        if len(usercheck)>0:


            user = authenticate(request,username=username,password=password)
            
            if user is not None:
                
                
                
                if user.userfor == 'beta':
                    
                    messages.success(request,'Login Successful')
                    djlogin(request,user)
                    return redirect('index')
                    
                if user.userfor == 'gamma':
                    
                    messages.success(request,'Login Successful')
                    djlogin(request,user)
                    return redirect('gamma')
                    
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
                if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email).exists():
                    messages.error(request,'Username or Email already exists')
                    return redirect('signup')
                else:
                    
                    if level == '1':
                        user=CustomUser.objects.create_user(username=username,email=email,password=password,userfor='beta')
                        BetaUser.objects.create(user=user)
                    if level == '2':
                        user=CustomUser.objects.create_user(username=username,email=email,password=password,userfor='gamma')
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
            user.profilepic=request.FILES['profilepic']
            
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

def dashboard(request):
    return render(request,'beta_admin/dashboard.html')