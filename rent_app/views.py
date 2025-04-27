from django.shortcuts import render, redirect
from django.db import connection

def list_properties(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM Property')
        properties = cursor.fetchall()
    return render(request, 'properties_list.html', {'properties': properties})


def create_property(request):
    if request.method == 'POST':
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
        owner_id = request.POST['owner_id']
        developer_id = request.POST['developer_id']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Property (
                    property_type, location, primary_market, area, room_count, floor, address, price, 
                    status, description, owner_id, developer_id
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                property_type, location, primary_market, area, room_count, floor,
                address, price, status, description, owner_id, developer_id
            ])
        return redirect('list_properties')

    return render(request, 'create_property.html')