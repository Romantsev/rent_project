from django.shortcuts import redirect
from django.db import connection
from django.http import HttpResponse
from datetime import date, datetime
import json

def date_handler(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM property")
        property_data = cursor.fetchall()
        property_cols = [col[0] for col in cursor.description]
        
        cursor.execute("SELECT * FROM inspection")
        inspection_data = cursor.fetchall()
        inspection_cols = [col[0] for col in cursor.description]

        cursor.execute("SELECT * FROM developer")
        developer_data = cursor.fetchall()
        developer_cols = [col[0] for col in cursor.description]

    data = {
        "properties": [dict(zip(property_cols, row)) for row in property_data],
        "developers": [dict(zip(developer_cols, row)) for row in developer_data],
        "inspections": [dict(zip(inspection_cols, row)) for row in inspection_data]
    }

    response = HttpResponse(json.dumps(data, indent=2, default=date_handler), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename="backup.json"'
    return response

def import_json(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        data = json.load(json_file)

        with connection.cursor() as cursor:
            for dev in data.get('developers', []):
                cursor.execute("""
                    INSERT INTO developer (developer_id, name, address, phone_number)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (developer_id) DO NOTHING
                """, [dev['developer_id'], dev['name'], dev['address'], dev['phone_number']])

            for prop in data.get('properties', []):
                cursor.execute("""
                    INSERT INTO property (
                        property_id, property_type, location, primary_market, area,
                        room_count, floor, address, price, status, description,
                        owner_id, developer_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (property_id) DO NOTHING
                """, [
                    prop['property_id'], prop['property_type'], prop['location'], prop['primary_market'],
                    prop['area'], prop['room_count'], prop['floor'], prop['address'], prop['price'],
                    prop['status'], prop['description'], prop['owner_id'], prop['developer_id']
                ])
            
            for insp in data.get('inspections', []):
                cursor.execute("""
                    INSERT INTO inspection (inspection_id, property_id, inspection_date, property_condition)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (inspection_id) DO NOTHING
                """, [insp['inspection_id'], insp['property_id'], insp['inspection_date'], insp['property_condition']])
                
        return redirect('list_properties')

    return redirect('list_properties')

