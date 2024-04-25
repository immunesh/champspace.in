from django.shortcuts import render

# Create your views here.

def gammaAdmin(request):
    return render(request, 'gamma-admin/dashboard.html')