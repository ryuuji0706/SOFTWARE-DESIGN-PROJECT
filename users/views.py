from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def register_user(request):
    # If the user is already logged in, send them straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        # 1. Check if passwords match
        if password != confirm:
            messages.error(request, "Passwords do not match!")
            return redirect('register')
        
        # 2. Check if username already exists
        if User.objects.filter(username=name).exists():
            messages.error(request, "That name is already taken. Please choose another.")
            return redirect('register')

        # 3. Create the user securely
        user = User.objects.create_user(username=name, email=email, password=password)
        user.save()

        # 4. Automatically log them in after registering
        login(request, user)
        
        # 5. Send them to the dashboard!
        return redirect('dashboard')

    return render(request, 'users/register.html')

def login_user(request):
    # If they are already logged in, send them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate directly with Django's built-in system
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login')

    return render(request, 'users/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')