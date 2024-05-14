from django.shortcuts import render

# Create your views here.

def gammaUser(request):
    return render(request, 'gamma-user/dashboard.html')

def gammaMessages(request):
    return render(request, 'gamma-user/messages.html')

def gammaChat(request):
    return render(request, 'gamma-user/chat.html')