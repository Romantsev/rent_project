from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  

urlpatterns = [
    path('', lambda request: redirect('rent/', permanent=True)),
    path('admin/', admin.site.urls),
    path('rent/', include('rent_app.urls')),
]
