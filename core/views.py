from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact-us.html')

def faqs(request):
    return render(request, 'index.html')

def privacy_policy(request):
    return render(request, 'index.html')

def terms_and_conditions(request):
    return render(request, 'index.html')

def signIn(request):
    return render(request, 'sign-in.html')

def singUp(request):
    return render(request, 'sign-up.html')

def forget_password(request):
    return render(request, 'forgot-password.html')