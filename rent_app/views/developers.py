from django.shortcuts import render, redirect
from django.db import connection

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
 
def list_developers(request):
   with connection.cursor() as cursor:
      cursor.execute("""
         SELECT name, address, phone_number, developer_id
         FROM public.developer
      """)
      developers = cursor.fetchall()
   return render(request, 'developers_list.html', {'developers': developers})

def view_developer(request, developer_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM developer WHERE developer_id = %s", [developer_id])
        developer = cursor.fetchone()

        cursor.execute("""
            SELECT property_id, property_type, location, status
            FROM property
            WHERE developer_id = %s
        """, [developer_id])
        properties = cursor.fetchall()

    return render(request, 'view_developer.html', {'developer': developer, 'properties': properties})

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

def clear_developers(request):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM inspection")
        cursor.execute("DELETE FROM property")
        cursor.execute("DELETE FROM developer")
    return redirect('list_developers')
