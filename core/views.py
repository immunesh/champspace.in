from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.http import JsonResponse,HttpResponseRedirect,HttpResponse
from django.urls import reverse


# Create your views here.
def home(request):
    return render(request, 'index.html')



def forget_password(request):
    return render(request, 'forgot-password.html')

def student_dashboard(request):
    return render(request,'student-dashboard.html')


def signUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user,backend='core.backends.email_backend.EmailBackend')
            return JsonResponse({'success': True, 'redirect_url': reverse('sign-in')})  # Return a success response with redirect URL
            # return HttpResponseRedirect(reverse('sign-in')) 
        else:
            # Return errors if the form is not valid
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = SignUpForm()
    
    return render(request, 'sign-up.html', {'form': form})


def signIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:  # Check if both email and password are provided
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': reverse('student-dashboard')})
            else:
                return JsonResponse({'success': False, 'errors': {'non_field_errors': ['Invalid email or password.']}}, status=400)
        else:
            return JsonResponse({'success': False, 'errors': {'non_field_errors': ['Email and password are required.']}}, status=400)
    
    return render(request, 'sign-in.html', {})



# def signIn(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)
#         if user is not None:

#             login(request, user)
#             return JsonResponse({'success': True, 'redirect_url': reverse('student-dashboard')})
#             # return HttpResponseRedirect(reverse('student-dashboard'))

#         else:
#             print("SOMEONE TRIED TO LOGIN AND FILED! ")
#             print("Usernme : {}  and PassWord : {}".format(email,password))

#             return JsonResponse({'success': False, 'errors': {'non_field_errors': ['Invalid email or password.']}}, status=400)
#     return render(request, 'sign-in.html',{})

# def user_login(request):

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(username=username,password=password)

#         if user:
#             if user.is_active:
#                 login(request,user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 return HttpResponseRedirect("ACCOUNT IS NOT ACTIVE")
#         else:
#             print("SOMEONE TRIED TO LOGIN AND FILED! ")
#             print("Usernme : {}  and PassWord : {}".format(username,password))
#             return HttpResponse("Invalid Login details supplied! ")
#     else:
#         return render(request,'basicapp/login.html',{}) 
