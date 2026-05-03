from django.shortcuts import render

# Create your views here.

def login_user(request):
    # We will build the actual login logic later
    return render(request, 'analytics/login.html') 

def register_user(request):
    # We will build the actual registration logic later
    return render(request, 'analytics/register.html')