from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponseNotFound

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

   if not inspection:
      return HttpResponseNotFound("Інспекція не знайдена")

   return render(request, 'edit_inspection.html', {
      'inspection': inspection,
      'inspection_id': inspection_id
   })


def delete_inspection(request, inspection_id):
   with connection.cursor() as cursor:
      cursor.execute("SELECT property_id FROM inspection WHERE inspection_id = %s", [inspection_id])
      prop_id = cursor.fetchone()[0]
      cursor.execute("DELETE FROM inspection WHERE inspection_id = %s", [inspection_id])
   return redirect('view_property', property_id=prop_id)
