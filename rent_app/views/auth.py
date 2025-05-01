from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)

        owner_type = request.POST['owner_type']
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone_number']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO owner (user_id, owner_type, name, address, phone_number)
                VALUES (%s, %s, %s, %s, %s)
            """, [user.id, owner_type, name, address, phone])

        login(request, user)
        return redirect('list_properties')
    
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('list_properties')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')
