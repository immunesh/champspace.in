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
    if request.user.is_superuser:
        users=CustomUser.objects.all().order_by('-date_joined')
        
        month_wise_joined = defaultdict(int)
        month_wise_active = defaultdict(int)
        activelist=[]
        joinedlist=[]
        monthlist=''
        for user in users:
                
            string1 = user.date_joined
            month_wise_joined[string1.strftime('%b')] += 1
            if not user.last_login:
                pass
            else:
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
        if len(profit)<2:
            profit.append(0)
            profit.append('No purchase')
        context = {'activedata':activelist,
                'joineddata':joinedlist,
                'months':monthlist[:-1],
                'recentUsers':recentJoinedusers,
                'courses':courses,
                'breakchartdata':data,
                'profit':profit[1],
                'profitmonth':profit[0] ,
                'totalearn':totalearnings
                }

        return render(request,'beta_admin/admin/dashboard.html', context=context)
    else:
        to=request.user.userfor
        return redirect(to)

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
                    return redirect('beta')
                    
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
    if not request.user.is_authenticated:
        return redirect('login')
    user=CustomUser.objects.get(id=id)
    betauser=BetaUser.objects.get(user=user)
    return render (request,'beta_admin/viewprofile.html',{'user':user,'betauser':betauser})
def editprofile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user=request.user
    betauser=BetaUser.objects.get(user=user)
    if request.method== 'POST':
        print(request.POST)
        if request.FILES.get('profilepic'):
            user.profilepic=request.FILES['profilepic']
            
        user.first_name=request.POST['first']
        user.last_name=request.POST['last']
        

        betauser.phone=request.POST['phone']
        betauser.birthday=request.POST['birthday']
        betauser.website=request.POST['website']
        betauser.state=request.POST['state']
        betauser.city=request.POST['city']
        betauser.degree=request.POST['degree']
        betauser.grad_year=request.POST['grad_year']
        betauser.job_status=request.POST['status']
        betauser.profile_updated=True
        user.save()
        betauser.save()
        messages.success(request,'Profile Updated Successfully')
        return redirect('editprofile')
    
    return render(request,'beta_admin/editprofile.html',{'user':user,'betauser':betauser})


def home(request):
    if request.user.is_authenticated:
        beta_user=BetaUser.objects.get(user=request.user)
        if beta_user.profile_updated:
            return redirect('dashboard')
        else:
            messages.error(request,"Please Update Your Profile")
            return redirect('editprofile')
    else:
        return redirect('index')
from .emailsnder import *
import uuid
def forget(request):
    if request.method == 'POST':
        email=request.POST['email']
        if CustomUser.objects.filter(email=email).exists():
            user=CustomUser.objects.get(email=email)
            token=str(uuid.uuid4())
            user.token=token
            user.save()
            cofirm=send_forgot_mail(email,token)
            if cofirm:
                messages.success(request,'Email sent successfully')
                return redirect('login')
            else:
                messages.error(request,'Email not sent')
                return redirect('forgot')
        else:
            messages.error(request,'Username not found')
            return redirect('forgot')
    return render(request,'beta_admin/forgot_passwordhelper.html')
def forgotreset(request,token):
    if request.method == 'POST':
        password1=request.POST['password1']
        password2=request.POST['password2']
        if password1==password2:
            if CustomUser.objects.filter(token=token).exists():

                user=CustomUser.objects.get(token=token)
                user.set_password(password1)
                user.save()
                messages.success(request,'Password reset successfully')
                return redirect('login')
            else:
                messages.error(request,'Invalid URL')
                return redirect('reset',token)
        else:
            messages.error(request,'Passwords do not match')
            return redirect('reset',token)
    return render(request,'beta_admin/password reset.html')
def inbox(request):
    return render(request,'beta_admin/inbox.html')
def dashboard(request):
    courses=isPurchased.objects.filter(buyer=request.user)
    completed=Progress.objects.filter(user=request.user,progress=100)
    progress=Progress.objects.filter(user=request.user)
    progress=zip(courses,progress)
    
    context={'courses':courses,'completed':completed,'progresses':progress}
    return render(request,'beta_admin/dashboard.html',context)
def mycourses(request):
    courses=isPurchased.objects.filter(buyer=request.user)
    completed=Progress.objects.filter(user=request.user,progress=100)
    progress=Progress.objects.filter(user=request.user)
    progress=zip(courses,progress)
    
    context={'courses':courses,'completed':completed,'progresses':progress}
    return render(request,'beta_admin/mycourses.html',context)
def quiz(request):
    return render(request,'beta_admin/quiz.html')
def subscriptions(request):
    return render(request,'beta_admin/subscription.html')
def settings(request):
    return render(request,'beta_admin/settings.html')

def courses(request):
    course_details=Course.objects.all()
    category=[]
    for i in course_details:
        if i.course_category in category:
            continue
        else:

            category.append(i.course_category)

    return render(request,'beta_admin/courses.html',{'course':course_details,'categories':category})
def admincourses(request):
    courses=Course.objects.all()
    purchases=isPurchased.objects.all()
    freecourses=courses.filter(course_price=0)
    return render(request,'beta_admin/admin/courses.html',{'courses':courses,"purchases":purchases,'free':freecourses })
def admincourseadd(request,pk):
    if pk!= 'add':
        course=Course.objects.get(id=pk)
        purchases=isPurchased.objects.filter(course=course)
        progress=[]
        for i in purchases:
            progress.append(Progress.objects.get(user=i.buyer,course=course))
        purchases1=zip(purchases,progress)
        purch=isPurchased.objects.filter(course=course)
        return render(request,'beta_admin/admin/course-details.html',{'course':course,'purchases':purchases1,'pr':purch})
    else:
        if request.method == 'POST':
            if request.FILES.get('video') and request.FILES.get('image'):
                ctreated_course=Course.objects.create(course_level=request.POST['level'],video=request.FILES['video'],course_image=request.FILES['image'],course_name=request.POST['title'],course_instructor=request.user,course_duration=request.POST['duration'],course_description=request.POST['description'],course_price=request.POST['price'],lectures=request.POST['lectures'],course_category=request.POST['category'])
                ctreated_course.save()
                messages.success(request,'Course uploaded')
                return redirect('admincourses')
        return render(request,'beta_admin/admin/course-add.html')
def courseedit(request,pk):
    course=Course.objects.get(id=pk)
    if request.method=='POST':
        course.course_category=request.POST['category']
        course.course_description=request.POST['description']
        course.course_price=request.POST['price']
        course.course_duration=request.POST['duration']
        course.course_level=request.POST['level']
        course.course_name=request.POST['title']
        course.lectures=request.POST['lectures']
        course.save()
        return redirect('admincourses')
    return render(request,'beta_admin/admin/course-edit.html',{'course':course})
def delcourse(request,pk):
    course=Course.objects.get(id=pk)
    course.delete()
    return redirect(request.META['HTTP_REFERER'])
def userlist(request):
    customusers=CustomUser.objects.all()
    betusers=BetaUser.objects.all()
    purchased=[]
    for i in customusers:
        if isPurchased.objects.filter(buyer=i).exists():
            purchased.append(True)
        else:
            purchased.append(False)
    users=zip(customusers,betusers,purchased)
    
    return render(request,'beta_admin/admin/users.html',{'users':users})
def deluser(request,pk):
    user=CustomUser.objects.get(id=pk)
    user.delete()
    return redirect(request.META['HTTP_REFERER'])
def usercreation(request):
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password1']
        if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Username or Email already exists')
            return redirect('usercreate')
        else:
            
        
            user=CustomUser.objects.create_user(username=username,email=email,password=password,userfor='beta')
            BetaUser.objects.create(user=user)
            messages.success(request,'Account Created Successfully')
            return redirect('userslist')
    return render(request,'beta_admin/admin/usercreation.html')
def listmessages(request):
    user=request.user
    betauser=BetaUser.objects.get(user=user)
    chatbox=Chatbox.objects.filter(sender=betauser ) | Chatbox.objects.filter(receiver=betauser)
    
    return render(request,'beta_admin/messages-page.html',{'chatbox':chatbox,'betauser':betauser})
def getmessages(request,pk):
    user=request.user
    betauser=BetaUser.objects.get(user=user)
    chatbox1=Chatbox.objects.filter(sender=betauser ) | Chatbox.objects.filter(receiver=betauser)
    chat1=Chatbox.objects.get(id=pk)
    chat=Chat.objects.filter(chatbox=chat1)
    receiver=0
    if chat1.sender==betauser:
        receiver=chat1.receiver.id
    else:
        receiver=chat1.sender.id

    return render(request,'beta_admin/getmessages-page.html',{'chatbox':chatbox1,'betauser':betauser,'chats':chat,'chat1':chat1,'receiver':receiver})
def adminmsgs(request):
    msgs=Chat.objects.all().order_by('-created_at')
    return render(request,'beta_admin/admin/messageslist.html',{'msgs':msgs})
def delmsg(request,pk):
    msg=Chat.objects.get(id=pk)
    msg.delete()
    return redirect(request.META['HTTP_REFERER'])