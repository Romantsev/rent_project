from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import logout

def list_owners(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public.owner')
        owners = cursor.fetchall()
    return render(request, 'owners_list.html', {'owners': owners})

def view_profile(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT owner_id, user_id, owner_type, name, address, phone_number
            FROM owner
            WHERE user_id = %s
        """, [user_id])
        row = cursor.fetchone()
        if not row:
            return render(request, 'not_found.html')

        owner = {
            'owner_id': row[0],
            'user_id': row[1],
            'owner_type': row[2],
            'name': row[3],
            'address': row[4],
            'phone_number': row[5]
        }

        cursor.execute("""
            SELECT p.property_id, p.property_type, p.location, p.status
            FROM property p
            JOIN owner o ON p.owner_id = o.owner_id
            WHERE o.user_id = %s
        """, [user_id])
        properties = cursor.fetchall()

    is_owner = request.user.is_authenticated and request.user.id == owner['user_id']

    return render(request, 'view_profile.html', {
        'owner': owner,
        'properties': properties,
        'is_owner': is_owner
    })

def edit_profile(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT owner_id, user_id, owner_type, name, address, phone_number
            FROM owner
            WHERE user_id = %s
        """, [user_id])
        row = cursor.fetchone()

    if not row:
        return render(request, 'not_found.html')

    owner = {
        'owner_id': row[0],
        'user_id': row[1],
        'owner_type': row[2],
        'name': row[3],
        'address': row[4],
        'phone_number': row[5]
    }

    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE owner
                SET name=%s, address=%s, phone_number=%s
                WHERE user_id=%s
            """, [name, address, phone_number, user_id])

        return redirect('view_profile', user_id=user_id)

    return render(request, 'edit_profile.html', {'owner': owner})

def delete_profile(request, user_id):
   logout(request)

   with connection.cursor() as cursor:
      cursor.execute("DELETE FROM inspection WHERE property_id IN (SELECT property_id FROM property WHERE owner_id = (SELECT owner_id FROM owner WHERE user_id = %s))", [user_id])
      cursor.execute("DELETE FROM property WHERE owner_id = (SELECT owner_id FROM owner WHERE user_id = %s)", [user_id])
      cursor.execute("DELETE FROM owner WHERE user_id = %s", [user_id])
      cursor.execute("DELETE FROM rent_app_customuser WHERE id = %s", [user_id])

   return redirect('login')