from django.shortcuts import render, redirect
from django.db import connection
from django.db import IntegrityError

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
    sort = request.GET.get("sort", "property_id")

    query = """
        SELECT 
            property_type, location, primary_market, status,
            owner_name, developer_name, property_id, owner_id, user_id, developer_id
        FROM property_view
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (location ILIKE %s OR developer_name ILIKE %s OR status ILIKE %s)"
        params.extend([f"%{search}%"] * 3)

    if filter_status:
        query += " AND status = %s"
        params.append(filter_status)

    if filter_type:
        query += " AND property_type = %s"
        params.append(filter_type)

    if filter_market:
        query += " AND primary_market = %s"
        params.append(filter_market)

    allowed_sorts = {
        "price": "price",
        "status": "status",
        "location": "location",
        "type": "property_type"
    }
    sort_column = allowed_sorts.get(sort, "property_id")
    query += f" ORDER BY {sort_column} ASC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        properties = [dict(zip(columns, row)) for row in rows]  # Преобразуем в список словарей

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
def view_property(request, property_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.property_id, p.property_type, p.location, p.primary_market, p.area,
                p.room_count, p.floor, p.address, p.price, p.status, p.description,
                p.owner_id, p.developer_id,
                o.name AS owner_name, o.user_id,
                d.name AS developer_name
            FROM property p
            LEFT JOIN owner o ON p.owner_id = o.owner_id
            LEFT JOIN developer d ON p.developer_id = d.developer_id
            WHERE p.property_id = %s
        """, [property_id])
        
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        property_data = dict(zip(columns, row))

        cursor.execute("""
            SELECT inspection_id, inspection_date, property_condition
            FROM inspection
            WHERE property_id = %s
            ORDER BY inspection_date DESC
        """, [property_id])
        rows = cursor.fetchall()
        inspections = [
            {
                'inspection_id': row[0],
                'inspection_date': row[1],
                'property_condition': row[2]
            }
            for row in rows
        ]

    is_owner = False
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute("SELECT owner_id FROM owner WHERE user_id = %s", [request.user.id])
            owner_result = cursor.fetchone()
            if owner_result and owner_result[0] == property_data['owner_id']:
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

def clear_properties(request):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM inspection")
        cursor.execute("DELETE FROM property")
    return redirect('list_properties')
