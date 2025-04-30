from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def list_properties(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.property_type, 
                p.location, 
                p.primary_market, 
                p.status, 
                o.name AS owner_name, 
                d.name AS developer_name
            FROM 
                Property p
            JOIN owner o ON p.owner_id = o.owner_id
            JOIN developer d ON p.developer_id = d.developer_id
        """)
        properties = cursor.fetchall()
    return render(request, 'properties_list.html', {'properties': properties})

def create_property(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT owner_id FROM owner WHERE user_id = %s", [request.user.id])
            owner_result = cursor.fetchone()
            if not owner_result:
                return render(request, 'create_property.html', {'error': 'Owner not found'})
            owner_id = owner_result[0]

        property_type = request.POST['property_type']
        location = request.POST['location']
        primary_market = request.POST['primary_market']
        area = request.POST['area']
        room_count = request.POST['room_count']
        floor = request.POST['floor']
        address = request.POST['address']
        price = request.POST['price']
        status = request.POST['status']
        description = request.POST['description']
        developer_id = request.POST['developer_id']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO property (
                    property_type, location, primary_market, area, room_count, floor, address, price, 
                    status, description, owner_id, developer_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                property_type, location, primary_market, area, room_count, floor, address,
                price, status, description, owner_id, developer_id
            ])
        return redirect('list_properties')

    with connection.cursor() as cursor:
        cursor.execute("SELECT developer_id, name FROM developer")
        developers = cursor.fetchall()

    return render(request, 'create_property.html', {'developers': developers})

def view_property(request, property_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.*, o.name, d.name
            FROM property p
            LEFT JOIN owner o ON p.owner_id = o.owner_id
            LEFT JOIN developer d ON p.developer_id = d.developer_id
            WHERE p.property_id = %s
        """, [property_id])
        property_data = cursor.fetchone()
    return render(request, 'view_property.html', {'property': property_data})


def list_owners(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public.owner')
        owners = cursor.fetchall()
    return render(request, 'owners_list.html', {'owners': owners})

def create_owner(request):
    if request.method == 'POST':
        owner_type = request.POST['owner_type']
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.owner (owner_type, name, address, phone_number)
                VALUES (%s, %s, %s, %s)
            """, [owner_type, name, address, phone_number])
        return redirect('list_owners')

    return render(request, 'create_owner.html')

def list_developers(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public.developer')
        developers = cursor.fetchall()
    return render(request, 'developers_list.html', {'developers': developers})

def create_developer(request):
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.developer (name, address, phone_number)
                VALUES (%s, %s, %s)
            """, [name, address, phone_number])
        return redirect('list_developers')

    return render(request, 'create_developer.html')

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