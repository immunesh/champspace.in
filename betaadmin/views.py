# Create your views here.
from django.shortcuts import render
from base.models import CustomUser,Course,isPurchased
from collections import defaultdict

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