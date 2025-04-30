from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.db import IntegrityError

def list_properties(request):
    user_owner_id = None
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute("SELECT owner_id FROM owner WHERE user_id = %s", [request.user.id])
            result = cursor.fetchone()
            if result:
                user_owner_id = result[0]

    search = request.GET.get("search", "").strip()
    filter_status = request.GET.get("status", "")
    filter_type = request.GET.get("type", "")
    filter_market = request.GET.get("market", "")
    sort = request.GET.get("sort", "p.property_id")

    query = """
        SELECT 
            p.property_type, p.location, p.primary_market, p.status,
            o.name AS owner_name, d.name AS developer_name, p.property_id, p.owner_id
        FROM 
            Property p
        JOIN owner o ON p.owner_id = o.owner_id
        JOIN developer d ON p.developer_id = d.developer_id
        WHERE 1=1
    """

    params = []

    if search:
        query += " AND (p.location ILIKE %s OR d.name ILIKE %s OR p.status ILIKE %s)"
        params.extend([f"%{search}%"] * 3)

    if filter_status:
        query += " AND p.status = %s"
        params.append(filter_status)

    if filter_type:
        query += " AND p.property_type = %s"
        params.append(filter_type)

    if filter_market:
        query += " AND p.primary_market = %s"
        params.append(filter_market)

    allowed_sorts = {
        "price": "p.price",
        "status": "p.status",
        "location": "p.location",
        "type": "p.property_type"
    }
    sort_column = allowed_sorts.get(sort, "p.property_id")

    query += f" ORDER BY {sort_column} ASC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        properties = cursor.fetchall()

    return render(request, 'properties_list.html', {
        'properties': properties,
        'user_owner_id': user_owner_id,
        'filters': {
            'search': search,
            'status': filter_status,
            'type': filter_type,
            'market': filter_market,
            'sort': sort
        }
    })


def create_property(request):
    errors = []
    developers = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT developer_id, name FROM developer")
        developers = cursor.fetchall()

    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT owner_id FROM owner WHERE user_id = %s", [request.user.id])
                owner_result = cursor.fetchone()
                if not owner_result:
                    errors.append("Owner not found.")
                    return render(request, 'create_property.html', {'developers': developers, 'errors': errors})
                owner_id = owner_result[0]

            required_fields = ['property_type', 'location', 'primary_market', 'area', 'room_count', 'floor',
                               'address', 'price', 'status', 'developer_id']

            for field in required_fields:
                if not request.POST.get(field):
                    errors.append(f"Field '{field.replace('_', ' ').capitalize()}' is required.")

            if errors:
                return render(request, 'create_property.html', {'developers': developers, 'errors': errors})

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO property (
                        property_type, location, primary_market, area, room_count, floor, address, price, 
                        status, description, owner_id, developer_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    request.POST['property_type'],
                    request.POST['location'],
                    request.POST['primary_market'],
                    float(request.POST['area']),
                    int(request.POST['room_count']),
                    int(request.POST['floor']),
                    request.POST['address'],
                    float(request.POST['price']),
                    request.POST['status'],
                    request.POST.get('description', ''),
                    owner_id,
                    int(request.POST['developer_id'])
                ])
            return redirect('list_properties')

        except (ValueError, IntegrityError) as e:
            errors.append(f"Error: {str(e)}")

    return render(request, 'create_property.html', {'developers': developers, 'errors': errors})

def view_property(request, property_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.*, o.name, d.name, p.owner_id
            FROM property p
            LEFT JOIN owner o ON p.owner_id = o.owner_id
            LEFT JOIN developer d ON p.developer_id = d.developer_id
            WHERE p.property_id = %s
        """, [property_id])
        property_data = cursor.fetchone()

        cursor.execute("""
            SELECT inspection_date, property_condition
            FROM inspection
            WHERE property_id = %s
            ORDER BY inspection_date DESC
        """, [property_id])
        inspections = cursor.fetchall()

    is_owner = False
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute("SELECT owner_id FROM owner WHERE user_id = %s", [request.user.id])
            owner_result = cursor.fetchone()
            if owner_result and owner_result[0] == property_data[-1]:
                is_owner = True

    return render(request, 'view_property.html', {
        'property': property_data,
        'inspections': inspections,
        'is_owner': is_owner
    })


def edit_property(request, property_id):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            cursor.execute("""
                UPDATE property SET property_type=%s, location=%s, primary_market=%s,
                area=%s, room_count=%s, floor=%s, address=%s, price=%s, status=%s, description=%s, developer_id=%s
                WHERE property_id=%s
            """, [
                request.POST['property_type'],
                request.POST['location'],
                request.POST['primary_market'],
                request.POST['area'],
                request.POST['room_count'],
                request.POST['floor'],
                request.POST['address'],
                request.POST['price'],
                request.POST['status'],
                request.POST['description'],
                request.POST['developer_id'],
                property_id
            ])
            return redirect('list_properties')
        else:
            cursor.execute("SELECT * FROM property WHERE property_id = %s", [property_id])
            prop = cursor.fetchone()
            cursor.execute("SELECT developer_id, name FROM developer")
            developers = cursor.fetchall()
    return render(request, 'edit_property.html', {'property': prop, 'developers': developers})

def delete_property(request, property_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM property WHERE property_id = %s", [property_id])
    return redirect('list_properties')

def list_owners(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public.owner')
        owners = cursor.fetchall()
    return render(request, 'owners_list.html', {'owners': owners})

def list_developers(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name, address, phone_number, developer_id
            FROM public.developer
        """)
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

def edit_developer(request, developer_id):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            name = request.POST['name']
            address = request.POST['address']
            phone_number = request.POST['phone_number']
            cursor.execute("""
                UPDATE developer SET name=%s, address=%s, phone_number=%s
                WHERE developer_id=%s
            """, [name, address, phone_number, developer_id])
            return redirect('list_developers')
        else:
            cursor.execute("SELECT * FROM developer WHERE developer_id = %s", [developer_id])
            developer = cursor.fetchone()
    return render(request, 'edit_developer.html', {'developer': developer})

def delete_developer(request, developer_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM property WHERE developer_id = %s", [developer_id])
        cursor.execute("DELETE FROM developer WHERE developer_id = %s", [developer_id])
    return redirect('list_developers')

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

def add_inspection(request, property_id):
    if request.method == 'POST':
        inspection_date = request.POST['inspection_date']
        property_condition = request.POST['property_condition']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO inspection (property_id, inspection_date, property_condition)
                VALUES (%s, %s, %s)
            """, [property_id, inspection_date, property_condition])
        return redirect('view_property', property_id=property_id)

    return render(request, 'add_inspection.html', {'property_id': property_id})

def edit_inspection(request, inspection_id):
    if request.method == 'POST':
        inspection_date = request.POST['inspection_date']
        property_condition = request.POST['property_condition']
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE inspection SET inspection_date=%s, property_condition=%s
                WHERE inspection_id=%s
            """, [inspection_date, property_condition, inspection_id])
            cursor.execute("SELECT property_id FROM inspection WHERE inspection_id = %s", [inspection_id])
            prop_id = cursor.fetchone()[0]
        return redirect('view_property', property_id=prop_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT inspection_date, property_condition, property_id FROM inspection WHERE inspection_id = %s", [inspection_id])
        inspection = cursor.fetchone()
    return render(request, 'edit_inspection.html', {'inspection': inspection, 'inspection_id': inspection_id})

def delete_inspection(request, inspection_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT property_id FROM inspection WHERE inspection_id = %s", [inspection_id])
        prop_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM inspection WHERE inspection_id = %s", [inspection_id])
    return redirect('view_property', property_id=prop_id)
